import nest
from influxdb import InfluxDBClient
from nest.utils import c_to_f

class InfluxNestEmitter(object):
  def __init__(self, nest, influx):
    """
    Inputs:
      nest: An instance of the Nest object.
      influx: An intance of the InfluxDBClient.
    """

    self.nest = nest
    self.influx = influx

  def emit_event(self):
    structure = next(iter(self.nest.structures))
    device = next(iter(structure.devices))
    weather = structure.weather

    json_body = [{
      "measurement": "nest",
      "fields": {
        "indoor_temperature": c_to_f(device.temperature),
        "indoor_humidity": device.humidity,
        "target_indoor_temperature": c_to_f(device.target),
        "outdoor_temperature": c_to_f(weather.current.temperature),
        "outdoor_humidity": weather.current.humidity,
        "wind_speed": weather.current.wind.kph,

      },
      "tags": {
        "wind_direction": weather.current.wind.direction,
        "mode": device.mode,
        "fan": device.fan,
      },
    }]

    self.influx.write_points(json_body)


if __name__ == "__main__":
  import os
  import time

  NEST_USERNAME = os.getenv("NEST_USERNAME")
  NEST_PASSWORD = os.getenv("NEST_PASSWORD")
  INFLUX_HOST = os.getenv("INFLUX_HOST", "influxdb")
  INFLUX_PORT = int(os.getenv("INFLUX_PORT", "8086"))
  INFLUX_USERNAME = os.getenv("INFLUX_USERNAME")
  INFLUX_PASSWORD = os.getenv("INFLUX_PASSWORD")
  INFLUX_DB_NAME = os.getenv("INFLUX_DB_NAME", "metrics")

  influx_client = InfluxDBClient(
    INFLUX_HOST,
    INFLUX_PORT,
    INFLUX_USERNAME,
    INFLUX_PASSWORD,
    INFLUX_DB_NAME,
    )

  nest_client = nest.Nest(NEST_USERNAME, NEST_PASSWORD)

  data_emitter = InfluxNestEmitter(nest_client, influx_client)

  while True:
    try:
      data_emitter.emit_event()
      print("Event Emitted.")
      time.sleep(60)
    except Exception as e:
      print("Failed to emit. {}".format(e.message))
