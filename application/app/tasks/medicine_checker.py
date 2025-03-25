"""
Gyógyszer ellenőrző és értesítő modul.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from app.medicine.models import MedicineStock
from app.auth.models import User
from app.utils.email_sender import send_email

def check_medicines_and_notify(app):
    """
    Ellenőrzi a gyógyszereket és értesítést küld, ha valamelyik kiváltható
    """
    app.logger.info("Starting medicine check...")
    start_time = time.time()

    with app.app_context():
        try:
            # Ellenőrizzük, hogy engedélyezve van-e az ellenőrzés
            if not app.config['ENABLE_MEDICINE_CHECKER']:
                app.logger.info("Medicine checker is disabled in configuration")
                return

            user_medicines = {}
            
            # Minden aktív készlet ellenőrzése
            app.logger.debug("Checking active stocks for users")
            stocks = MedicineStock.objects()
            app.logger.debug(f"Found {stocks.count()} medicine stocks")

            for stock in stocks:
                if stock.can_refill():
                    user_id = stock.created_by.id
                    if user_id not in user_medicines:
                        user_medicines[user_id] = []
                    user_medicines[user_id].append({
                        'name': stock.medicine.name,
                        'current_quantity': stock.get_quantity_at_date(),
                        'days_remaining': stock.calculate_days_remaining(),
                        'warning_date': stock.calculate_warning_date()
                    })
            
            app.logger.debug(f"Found {len(user_medicines)} users with medicines to notify")

            # Értesítések küldése felhasználónként
            for user_id, medicines in user_medicines.items():
                try:
                    user = User.objects.get(id=user_id)
                    if medicines:
                        # Email szöveg összeállítása
                        medicines_text = "\n".join([
                            f"- {med['name']}: "
                            f"jelenlegi mennyiség: {med['current_quantity']}, "
                            f"még {med['days_remaining']} napra elegendő"
                            for med in medicines
                        ])

                        email_body = f"""Tisztelt {user.lastname} {user.firstname}!

Az alábbi gyógyszerek kiváltása esedékes:

{medicines_text}

Kérjük, lépjen be a rendszerbe a részletek megtekintéséhez.

Üdvözlettel,
medTrack - Gyógyszer Nyilvántartó Rendszer"""

                        # Email küldése
                        if send_email(
                            app=app,
                            recipient=user.email,
                            subject="Gyógyszer kiváltási értesítő",
                            body=email_body
                        ):
                            app.logger.info(f"Notification sent to {user.email}")
                        else:
                            app.logger.error(f"Failed to send notification to {user.email}")
                except Exception as e:
                    app.logger.error(f"Error processing user {user_id}: {str(e)}")

        except Exception as e:
            app.logger.error(f"Error in medicine checker: {str(e)}", exc_info=True)
        finally:
            end_time = time.time()
            duration = end_time - start_time
            app.logger.info(f"Medicine check completed in {duration:.2f} seconds")

def init_scheduler(app):
    """
    Ütemező inicializálása és feladat beállítása
    """
    app.logger.info("Initializing medicine checker scheduler...")
    
    if not app.config['ENABLE_MEDICINE_CHECKER']:
        app.logger.info("Medicine checker is disabled in configuration. Scheduler will not start.")
        return

    scheduler = BackgroundScheduler()
    check_interval = app.config['MEDICINE_CHECK_INTERVAL']
    
    scheduler.add_job(
        func=check_medicines_and_notify,
        args=[app],
        trigger=IntervalTrigger(minutes=check_interval),
        id='medicine_checker',
        name=f'Check medicines and send notifications every {check_interval} minutes',
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=None
    )
    
    scheduler.start()
    app.logger.info(f"Scheduler started - checking medicines every {check_interval} minutes")