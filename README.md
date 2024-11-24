# Secret Paisano

Secret Paisano is a Python-based application that automates the process of sending Secret Santa-style emails. This application reads participants' information from a CSV file, randomly pairs them, and sends out emails with details about their assigned "paisano" (gift recipient).

## Features

- **Random Pairing**: Randomly pairs participants for gift exchange.
- **Email Notifications**: Sends out emails to participants with details about their assigned paisano.
- **Custom Templates**: Uses a Jinja2 HTML template for email customization.
- **Backup**: Creates a backup of the participants and their pairings.

## Instalation

I used uv to create/use this app to use it you can simply run these commands:
```bash

uv sync
uv run main.py
```
## Requirements

- Python 3.7+
- pandas
- numpy
- Jinja2
- Pydantic
- pydantic-settings
- smtplib

To execute this command you need to put your environment variables and have a csv file with your friends data.
```csv
name,email,tshirt_size,colors,to_know,alergic
Paisano,paisano@gmail.com,L,#FFFFFF,"I love you so much guys",
```
