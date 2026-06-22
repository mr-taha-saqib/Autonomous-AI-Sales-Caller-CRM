"""Management CLI: `python -m app.cli seed` / `createsuperuser`.

Idempotent seeding of an admin user, sample reps, leads and demo data so the
dashboard has content on first boot.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.appointment import Appointment, AppointmentType
from app.models.call import Call, CallDirection, CallStatus
from app.models.lead import Lead, LeadStatus, LeadTemperature
from app.models.user import User, UserRole
from app.services.lead_scoring import score_lead


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed() -> None:
    create_tables()
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@algorixe.com").first():
            db.add(User(
                full_name="Algorixe Admin",
                email="admin@algorixe.com",
                hashed_password=hash_password("ChangeMe!123"),
                role=UserRole.ADMIN,
            ))
        if not db.query(User).filter(User.email == "rep@algorixe.com").first():
            db.add(User(
                full_name="Jordan Sales",
                email="rep@algorixe.com",
                hashed_password=hash_password("ChangeMe!123"),
                role=UserRole.AGENT,
                phone="+15551110000",
            ))
        db.commit()

        if db.query(Lead).count() == 0:
            samples = [
                ("Aisha Khan", "+15552001001", "aisha@example.com", "Dubai",
                 "AED 120,000", "Compact SUV", "1-3 months", True, False, "positive"),
                ("Mark Reyes", "+15552001002", "mark@example.com", "Austin",
                 "$45,000", "Electric sedan", "immediate", True, True, "positive"),
                ("Lena Park", "+15552001003", None, "Seoul",
                 None, "Used hatchback", "researching", False, False, "neutral"),
                ("Tom Boateng", "+15552001004", "tom@example.com", "London",
                 "£30,000", "Family minivan", "3-6 months", True, True, "neutral"),
            ]
            for (name, phone, email, loc, budget, vehicle, timeline,
                 fin, trade, sentiment) in samples:
                score, temp, prob = score_lead(
                    purchase_timeline=timeline, budget=budget,
                    vehicle_interest=vehicle, financing_need=fin,
                    trade_in_interest=trade, email=email, sentiment=sentiment,
                )
                db.add(Lead(
                    full_name=name, phone=phone, email=email, location=loc,
                    budget=budget, vehicle_interest=vehicle,
                    purchase_timeline=timeline, financing_need=fin,
                    trade_in_interest=trade, score=score, temperature=temp,
                    conversion_probability=prob, sentiment=sentiment,
                    status=LeadStatus.QUALIFIED if temp == LeadTemperature.HOT
                    else LeadStatus.CONTACTED,
                    source="seed",
                ))
            db.commit()

            lead = db.query(Lead).first()
            db.add(Call(
                direction=CallDirection.OUTBOUND, status=CallStatus.COMPLETED,
                from_number="+15551234567", to_number=lead.phone,
                duration_seconds=212, lead_id=lead.id,
                summary="Prospect interested in a compact SUV, booked a showroom visit.",
                key_intent="Buy compact SUV within 1-3 months",
                sentiment="positive", outcome="appointment_booked",
            ))
            db.add(Appointment(
                lead_id=lead.id,
                appointment_type=AppointmentType.SHOWROOM_VISIT,
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=2),
                location="Algorixe Showroom, Downtown",
                notes="Bring trade-in documents.",
            ))
            db.commit()
        print("✅ Seed complete. Admin: admin@algorixe.com / ChangeMe!123")
    finally:
        db.close()


def createsuperuser() -> None:
    create_tables()
    email = input("Email: ").strip().lower()
    name = input("Full name: ").strip()
    pw = input("Password: ").strip()
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print("User already exists.")
            return
        db.add(User(full_name=name, email=email,
                    hashed_password=hash_password(pw), role=UserRole.ADMIN))
        db.commit()
        print(f"✅ Admin {email} created.")
    finally:
        db.close()


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "seed"
    {"seed": seed, "createsuperuser": createsuperuser,
     "init": create_tables}.get(cmd, seed)()


if __name__ == "__main__":
    main()
