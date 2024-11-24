import logging
import pickle
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Literal, Optional

import numpy as np
import pandas as pd
from jinja2 import Environment as JinjaEnvironment
from jinja2 import FileSystemLoader
from pydantic import BaseModel, TypeAdapter, field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


class SecretPaisanoEnvironment(BaseSettings):
    test: bool = True
    app_name: str = ""

    random_images_url: str = ""

    mailer_email: str = ""
    mailer_key: str = ""
    mailer_host: str = "smtp.gmail.com"
    mailer_port: int = 587
    html_template_file: str = "email.html.jinja"

    csv_responses: str = "responses.csv"

    backup_path: str = "BACKUP_secret_paisano.pickle"


class Paisano(BaseModel):
    name: str
    email: str
    tshirt_size: Literal["XS", "S", "M", "L", "XL", "XXL", "?"]
    colors: List[str]
    to_know: Optional[str]
    alergic: Optional[str]

    @field_validator("colors", mode="before")
    @classmethod
    def colors_validator(cls, v: str) -> List[str]:
        return v.split(",")


class Couple(BaseModel):
    gifted: Paisano
    gifter: Paisano


class SecretPaisano:
    couples: List[Couple]
    environment: SecretPaisanoEnvironment
    paisanos: List[Paisano]
    template_env: JinjaEnvironment
    mailer: smtplib.SMTP

    def __init__(self, environment: SecretPaisanoEnvironment) -> None:
        self.environment = environment
        self.paisanos = self._get_paisanos_from_csv()
        self.couples = self._get_couples()
        self.template_env = JinjaEnvironment(loader=FileSystemLoader("./"))

    def _get_mailer(self) -> smtplib.SMTP:
        mailer = smtplib.SMTP(
            self.environment.mailer_host, self.environment.mailer_port
        )
        mailer.starttls()
        mailer.login(self.environment.mailer_email, self.environment.mailer_key)
        return mailer

    def _read_csv(self) -> pd.DataFrame:
        df = pd.read_csv(self.environment.csv_responses)
        df.replace({np.nan: None}, inplace=True)
        df.dropna(axis=0, how="all", inplace=True)
        return df

    def _get_paisanos_from_csv(self) -> List[Paisano]:
        df = self._read_csv()
        records = df.to_dict(orient="records")
        adapter = TypeAdapter(List[Paisano])
        return adapter.validate_python(records)

    def _get_couples(self) -> List[Couple]:
        random.shuffle(self.paisanos)
        couples = zip(self.paisanos, (self.paisanos[-1:] + self.paisanos[:-1]))
        return [Couple(gifter=gifter, gifted=gifted) for gifter, gifted in couples]

    def save(self) -> None:
        with open(self.environment.backup_path, "wb") as backup_file:
            pickle.dump(
                {"couples": self.couples, "paisanos": self.paisanos}, backup_file
            )

    def send(self) -> None:
        self.mailer = self._get_mailer()
        for couple in self.couples:
            self._send_email(couple)
        self.mailer.close()

    def _send_email(self, couple: Couple) -> None:
        email = self._build_email(couple)
        to = self._get_email(couple.gifter)
        self.mailer.sendmail(
            self.environment.mailer_email,
            to,
            email.as_string(),
        )
        logger.info(f"Sending email to {to}")

    def _build_email(self, couple) -> MIMEMultipart:
        msg = MIMEMultipart()
        to = self._get_email(couple.gifter)
        msg["From"] = self.environment.mailer_email
        msg["To"] = to
        msg["Subject"] = "Paisano invisible!!!!"

        msg.attach(MIMEText(self._render_email(couple), "html"))
        return msg

    def _get_email(self, paisano: Paisano) -> str:
        return self.environment.mailer_email if self.environment.test else paisano.email

    def _render_email(self, couple: Couple) -> str:
        template = self.template_env.get_template(self.environment.html_template_file)
        return template.render(
            couple=couple,
            random_image_url=self.environment.random_images_url,
        )


if __name__ == "__main__":
    environment = SecretPaisanoEnvironment()
    secret_paisano = SecretPaisano(environment)
    secret_paisano.save()
    secret_paisano.send()
