import pandas as pd
from sqlalchemy import create_engine

# Load the CSV file
df = pd.read_csv('full_products_glamira.csv')

# Create a connection to the database
engine = create_engine('postgresql+psycopg2://username:password@localhost:5432/yourdatabase')

# Write the data into the database
df.to_sql('glamira_products', con=engine, if_exists='append', index=False)

print(f"Successfully loaded {len(df)} rows into the database.")
