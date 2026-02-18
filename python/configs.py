from enum import Enum


class Topology(Enum):
    GATEWAY_ONLY = (1, "Gateway node only")
    GATEWAY_NOISE = (2, "Gateway and noise node")
    GATEWAY_AIR = (3, "Gateway and air quality node")
    GATEWAY_FULL = (4, "Gateway, noise, and air quality node")

    def __init__(self, id, description):
        self.id = id
        self.description = description

class Scenario(Enum):
    HEARTBEATS_ONLY = ("A", "Heartbeats only (5m)")
    MOCK_ALERTS_12M = ("B", "Heartbeats (5m) + Mock Alerts (12m)")
    MOCK_ALERTS_5M = ("C", "Heartbeats (5m) + Mock Alerts (5m)")

    def __init__(self, code, description):
        self.code = code
        self.description = description
