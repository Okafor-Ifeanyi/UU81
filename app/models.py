from email.policy import default
from sqlalchemy import TIMESTAMP, Column, Float, Integer, String, Boolean, ForeignKey
from itsdangerous import TimedSerializer as Serializer
from sqlalchemy_utils import EmailType, URLType
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base
from .config import settings
from .paystack import PayStack
import secrets


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(URLType, nullable=True, default= "default.jpg")
    space_allowed = Column(Integer, nullable=False)
    space_available = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    status = Column(Boolean, server_default='TRUE', nullable=False )
    start_date = Column(TIMESTAMP(timezone=True))
    end_date = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), 
                      nullable=False, server_default=text('now()')) 
    owner_id = Column(Integer, ForeignKey("users.id", 
                        ondelete="CASCADE"), nullable=False)
    owner = relationship("User")
                        

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    email = Column(EmailType, nullable=False, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    image_url = Column(URLType, nullable=True, default= "default.jpg")
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), 
                    nullable=False, server_default=text('now()'))
    phone_number = Column(Integer, nullable=False)
    admin = Column(Boolean, nullable=False)
    is_host = Column(Boolean, server_default='FALSE', nullable=False)

    def get_acces_token(self, expires_sec=1800):
        s = Serializer(settings.secret_key, expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(settings.secret_key)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        
        return User.query.get(user_id)

class Payment(Base): 
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="NO ACTION"), nullable=False)
    amount = Column(Float,nullable=False)
    verified = Column(Boolean, server_default='FALSE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                    nullable=False, server_default=text('now()'))

    class Meta:
        ordering = ("created_at")

    def __str__(self) -> str:
        return f"Payment: {self.amount}"

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self) -> int:
        return self.amount *100

    def verify_payment(self):
        paystack = PayStack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] /100 == self.amount:
                self.verified = True
            self.save()
        if self.verified:
            return True
        return False


class Booking(Base):
    __tablename__ = "bookings"
    # __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, nullable=False, primary_key=True)
    space = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey(
        "events.id", ondelete="CASCADE"), nullable=False)
    event = relationship("Event")
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User") 
    created_at = Column(TIMESTAMP(timezone=True),
                    nullable=False, server_default=text('now()'))

    
    # title = Column(String, nullable=False)
    # place_id = Column(Integer, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    # payment_id = Column(Integer, ForeignKey("payments.id", ondelete="NO ACTION"), nullable=False)

   

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)

class Review(Base):
    __tablename__ = "reviews"
 
    id = Column(Integer, primary_key=True, nullable=False)
    event_id = Column(Integer, ForeignKey(
        "events.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer)
    review_body = Column(String)


