# Databricks notebook source
dbutils.widgets.text("config_path", "configs/dev.yaml", "Config Path")
config_path = dbutils.widgets.get("config_path")

from src.common.config import load_config
from src.gold.dim_state import run as run_dim_state
from src.gold.dim_date import run as run_dim_date

config = load_config(config_path)
run_dim_state(spark, config)
run_dim_date(spark, config)
