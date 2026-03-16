"""
Однократная миграция данных из DBF-файлов VFP в SQLite.
Запуск: uv run python -m src.infrastructure.migration.migrate_dbf
"""

from pathlib import Path

from dbfread import DBF

from src.infrastructure.database.models import (
    Base,
    GuardScheduleModel,
    GuardedObjectModel,
    InspectionModel,
    LegalEntityModel,
    ObjectServiceModel,
    OrgSettingsModel,
)
from src.infrastructure.database.session import SessionLocal, engine

DATA_DIR = Path(__file__).parents[3] / "DATA"


def _str(val: object) -> str:
    if val is None:
        return ""
    return str(val).strip()


def _load_time_table(filename: str) -> dict[str, dict]:
    """Читает time_kts.dbf или time_pul.dbf в словарь {объект: данные}."""
    path = DATA_DIR / filename
    result: dict[str, dict] = {}
    if not path.exists():
        return result
    try:
        for row in DBF(str(path), encoding="cp1251", ignore_missing_memofile=True):
            name = _str(row.get("OBIEKT"))
            if name:
                result[name] = row
    except Exception as e:
        print(f"  Предупреждение при чтении {filename}: {e}")
    return result


def _parse_time(val: object) -> str:
    s = _str(val)
    # нормализуем строку времени HH:MM
    parts = s.replace(".", ":").split(":")
    if len(parts) >= 2:
        try:
            h = int(parts[0]) % 24
            m = int(parts[1]) % 60
            return f"{h:02d}:{m:02d}"
        except ValueError:
            pass
    return "00:00"


def migrate() -> None:
    print("Создаём таблицы SQLite...")
    Base.metadata.create_all(engine)

    db = SessionLocal()

    # Проверка — уже мигрировали?
    if db.query(LegalEntityModel).count() > 0:
        print("База данных уже содержит данные. Миграция пропущена.")
        db.close()
        return

    print("Читаем time-таблицы...")
    time_kts = _load_time_table("time_kts.dbf")
    time_pul = _load_time_table("time_pul.dbf")

    print("Читаем basa.dbf...")
    # Собираем юр. лица — группируем объекты по имени собственника
    legal_entity_map: dict[str, LegalEntityModel] = {}
    object_rows: list[dict] = []

    basa_path = DATA_DIR / "basa.dbf"
    for row in DBF(str(basa_path), encoding="cp1251", ignore_missing_memofile=True):
        sob = _str(row.get("SOB"))
        if not sob:
            continue
        object_rows.append(dict(row))
        if sob not in legal_entity_map:
            vid_dog = _str(row.get("VID_DOG", "")).strip()
            contract_type = "Контракт" if "контр" in vid_dog.lower() else "Договор"
            le = LegalEntityModel(
                name=sob,
                contract_type=contract_type,
                contract_number=int(row.get("NUM") or 0),
                code=int(row.get("KOD") or 0) or None,
            )
            db.add(le)
            legal_entity_map[sob] = le

    db.flush()
    print(f"  Юр. лиц: {len(legal_entity_map)}")

    print("Создаём объекты и виды охраны...")
    obj_count = 0
    svc_count = 0

    for row in object_rows:
        sob = _str(row.get("SOB"))
        le = legal_entity_map[sob]

        obj = GuardedObjectModel(
            legal_entity_id=le.id,
            name=_str(row.get("OBIEKT")),
            town=_str(row.get("TOWN")),
            street=_str(row.get("STREET")),
            phone=_str(row.get("TEL")),
            signatory=_str(row.get("PEOPLE")),
            accepted_date=row.get("D_PR"),
            is_archived=False,
        )
        db.add(obj)
        db.flush()
        obj_count += 1

        obj_name = obj.name

        # КТС
        if row.get("KTS"):
            svc = ObjectServiceModel(
                object_id=obj.id,
                service_type="КТС",
                date_from=row.get("D_N_K"),
                date_to=row.get("D_K_K"),
                tariff=0.0,
                period=12,
            )
            db.add(svc)
            db.flush()
            _attach_schedule(db, svc, time_kts.get(obj_name))
            svc_count += 1

        # ПЦН
        if row.get("PUL"):
            svc = ObjectServiceModel(
                object_id=obj.id,
                service_type="ПЦН",
                date_from=row.get("D_N_P"),
                date_to=row.get("D_K_P"),
                tariff=0.0,
                period=12,
            )
            db.add(svc)
            db.flush()
            _attach_schedule(db, svc, time_pul.get(obj_name))
            svc_count += 1

    print(f"  Объектов: {obj_count}, видов охраны: {svc_count}")

    print("Читаем обследования (obsled.dbf)...")
    obsled_path = DATA_DIR / "obsled.dbf"
    insp_count = 0
    if obsled_path.exists():
        # Строим обратный словарь имя объекта → id
        obj_name_map: dict[str, int] = {}
        for o in db.query(GuardedObjectModel).all():
            obj_name_map[o.name] = o.id

        try:
            for row in DBF(str(obsled_path), encoding="cp1251", ignore_missing_memofile=True):
                name = _str(row.get("OBIEKT"))
                d = row.get("DATA")
                if not name or not d or name not in obj_name_map:
                    continue
                insp = InspectionModel(
                    object_id=obj_name_map[name],
                    date=d,
                    inspector="",
                )
                db.add(insp)
                insp_count += 1
        except Exception as e:
            print(f"  Предупреждение при чтении obsled.dbf: {e}")

    print(f"  Обследований: {insp_count}")

    db.commit()
    db.close()
    print("Читаем настройки организации (nastr.dbf)...")
    nastr_path = DATA_DIR / "nastr.dbf"
    if nastr_path.exists() and db.query(OrgSettingsModel).count() == 0:
        rows = list(DBF(str(nastr_path), encoding="cp1251", ignore_missing_memofile=True))
        if rows:
            r = rows[0]
            db.add(OrgSettingsModel(
                chief_name=_str(r.get("FIO")),
                chief_title=_str(r.get("DOLG")).strip(),
                org_name=_str(r.get("PREDPR")),
            ))
            db.commit()
            print(f"  Организация: {_str(r.get('PREDPR'))[:60]}...")

    print("Миграция завершена.")


def _attach_schedule(db, svc: ObjectServiceModel, time_row: dict | None) -> None:
    if time_row is None:
        return
    sched = GuardScheduleModel(
        service_id=svc.id,
        work_start=_parse_time(time_row.get("NACH")),
        work_end=_parse_time(time_row.get("KON")),
        days_off=_str(time_row.get("VICH")) or "суб.,вск.,праз",
        workday_from=_parse_time(time_row.get("V_NACH")),
        workday_to=_parse_time(time_row.get("V_KON")),
        workday_count=int(time_row.get("DAY_V") or 0),
        preholiday_from=_parse_time(time_row.get("P_NACH")),
        preholiday_to=_parse_time(time_row.get("P_KON")),
        preholiday_count=int(time_row.get("DAY_P") or 0),
        holiday_from=_parse_time(time_row.get("R_NACH") or time_row.get("R")),
        holiday_to=_parse_time(time_row.get("R_KON") or time_row.get("R1")),
        holiday_count=int(time_row.get("DAY_R") or 0),
    )
    db.add(sched)


if __name__ == "__main__":
    migrate()
