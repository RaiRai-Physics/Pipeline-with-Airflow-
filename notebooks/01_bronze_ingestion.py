# Databricks notebook source
dbutils.widgets.text("config_path", "configs/dev.yaml", "Config Path")
config_path = dbutils.widgets.get("config_path")

from src.common.config import load_config
from src.bronze.bronze_cdc_state_weekly import run

config = load_config(config_path)
run(spark, config)
