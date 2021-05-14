import datetime
import json

from pymazda.controller import Controller
from pymazda.exceptions import MazdaConfigException

class Client:
    def __init__(self, email, password, region, websession=None):
        if email is None or len(email) == 0:
            raise MazdaConfigException("Invalid or missing email address")
        if password is None or len(password) == 0:
            raise MazdaConfigException("Invalid or missing password")

        self.controller = Controller(email, password, region, websession)

        self._cached_state = {}

    async def validate_credentials(self):
        await self.controller.login()
    
    async def get_vehicles(self):
        vec_base_infos_response = await self.controller.get_vec_base_infos()

        vehicles = []
        for i, current_vec_base_info in enumerate(vec_base_infos_response.get("vecBaseInfos")):
            current_vehicle_flags = vec_base_infos_response.get("vehicleFlags")[i]

            # Ignore vehicles which are not enrolled in Mazda Connected Services
            if current_vehicle_flags.get("vinRegistStatus") != 3:
                continue

            other_veh_info = json.loads(current_vec_base_info.get("Vehicle").get("vehicleInformation"))

            nickname = await self.controller.get_nickname(current_vec_base_info.get("vin"))
            
            vehicle = {
                "vin": current_vec_base_info.get("vin"),
                "id": current_vec_base_info.get("Vehicle", {}).get("CvInformation", {}).get("internalVin"),
                "nickname": nickname,
                "carlineCode": other_veh_info.get("OtherInformation", {}).get("carlineCode"),
                "carlineName": other_veh_info.get("OtherInformation", {}).get("carlineName"),
                "modelYear": other_veh_info.get("OtherInformation", {}).get("modelYear"),
                "modelCode": other_veh_info.get("OtherInformation", {}).get("modelCode"),
                "modelName": other_veh_info.get("OtherInformation", {}).get("modelName"),
                "automaticTransmission": other_veh_info.get("OtherInformation", {}).get("transmissionType") == "A",
                "interiorColorCode": other_veh_info.get("OtherInformation", {}).get("interiorColorCode"),
                "interiorColorName": other_veh_info.get("OtherInformation", {}).get("interiorColorName"),
                "exteriorColorCode": other_veh_info.get("OtherInformation", {}).get("exteriorColorCode"),
                "exteriorColorName": other_veh_info.get("OtherInformation", {}).get("exteriorColorName")
            }

            vehicles.append(vehicle)

        return vehicles

    async def get_vehicle_status(self, vehicle_id):
        vehicle_status_response = await self.controller.get_vehicle_status(vehicle_id)

        alert_info = vehicle_status_response.get("alertInfos")[0]
        remote_info = vehicle_status_response.get("remoteInfos")[0]

        latitude = remote_info.get("PositionInfo", {}).get("Latitude")
        if latitude is not None:
            latitude = latitude * (-1 if remote_info.get("PositionInfo", {}).get("LatitudeFlag") == 1 else 1)
        longitude = remote_info.get("PositionInfo", {}).get("Longitude")
        if longitude is not None:
            longitude = longitude * (1 if remote_info.get("PositionInfo", {}).get("LongitudeFlag") == 1 else -1)

        vehicle_status = {
            "lastUpdatedTimestamp": alert_info.get("OccurrenceDate"),
            "latitude": latitude,
            "longitude": longitude,
            "positionTimestamp": remote_info.get("PositionInfo", {}).get("AcquisitionDatetime"),
            "fuelRemainingPercent": remote_info.get("ResidualFuel", {}).get("FuelSegementDActl"),
            "fuelDistanceRemainingKm": remote_info.get("ResidualFuel", {}).get("RemDrvDistDActlKm"),
            "odometerKm": remote_info.get("DriveInformation", {}).get("OdoDispValue"),
            "doors": {
                "driverDoorOpen": alert_info.get("Door", {}).get("DrStatDrv") == 1,
                "passengerDoorOpen": alert_info.get("Door", {}).get("DrStatPsngr") == 1,
                "rearLeftDoorOpen": alert_info.get("Door", {}).get("DrStatRl") == 1,
                "rearRightDoorOpen": alert_info.get("Door", {}).get("DrStatRr") == 1,
                "trunkOpen": alert_info.get("Door", {}).get("DrStatTrnkLg") == 1,
                "hoodOpen": alert_info.get("Door", {}).get("DrStatHood") == 1,
                "fuelLidOpen": alert_info.get("Door", {}).get("FuelLidOpenStatus") == 1
            },
            "doorLocks": {
                "driverDoorUnlocked": alert_info.get("Door", {}).get("LockLinkSwDrv") == 1,
                "passengerDoorUnlocked": alert_info.get("Door", {}).get("LockLinkSwPsngr") == 1,
                "rearLeftDoorUnlocked": alert_info.get("Door", {}).get("LockLinkSwRl") == 1,
                "rearRightDoorUnlocked": alert_info.get("Door", {}).get("LockLinkSwRr") == 1,
            },
            "windows": {
                "driverWindowOpen": alert_info.get("Pw", {}).get("PwPosDrv") == 1,
                "passengerWindowOpen": alert_info.get("Pw", {}).get("PwPosPsngr") == 1,
                "rearLeftWindowOpen": alert_info.get("Pw", {}).get("PwPosRl") == 1,
                "rearRightWindowOpen": alert_info.get("Pw", {}).get("PwPosRr") == 1
            },
            "hazardLightsOn": alert_info.get("HazardLamp", {}).get("HazardSw") == 1,
            "tirePressure": {
                "frontLeftTirePressurePsi": remote_info.get("TPMSInformation", {}).get("FLTPrsDispPsi"),
                "frontRightTirePressurePsi": remote_info.get("TPMSInformation", {}).get("FRTPrsDispPsi"),
                "rearLeftTirePressurePsi": remote_info.get("TPMSInformation", {}).get("RLTPrsDispPsi"),
                "rearRightTirePressurePsi": remote_info.get("TPMSInformation", {}).get("RRTPrsDispPsi")
            }
        }

        cached_state = self.__get_cached_state(vehicle_id)

        door_lock_status = vehicle_status["doorLocks"]

        cached_state["api_timestamp"] = datetime.datetime.strptime(vehicle_status["lastUpdatedTimestamp"], "%Y%m%d%H%M%S").replace(tzinfo=datetime.timezone.utc)
        cached_state["api_lock_state"] = not (
            door_lock_status["driverDoorUnlocked"]
            or door_lock_status["passengerDoorUnlocked"]
            or door_lock_status["rearLeftDoorUnlocked"]
            or door_lock_status["rearRightDoorUnlocked"]
        )

        return vehicle_status

    def get_assumed_lock_state(self, vehicle_id):
        cached_state = self.__get_cached_state(vehicle_id)

        if not "assumed_lock_state" in cached_state and not "api_lock_state" in cached_state:
            return None

        if "assumed_lock_state" in cached_state and not "api_lock_state" in cached_state:
            return cached_state.get("assumed_lock_state")

        if not "assumed_lock_state" in cached_state and "api_lock_state" in cached_state:
            return cached_state.get("api_lock_state")

        now_timestamp = datetime.datetime.now(datetime.timezone.utc)

        if (
            "assumed_lock_state_timestamp" in cached_state
            and "api_timestamp" in cached_state
            and cached_state.get("assumed_lock_state_timestamp") > cached_state.get("api_timestamp")
            and (now_timestamp - cached_state.get("assumed_lock_state_timestamp")) < datetime.timedelta(seconds=300)
        ):
            return cached_state.get("assumed_lock_state")

        return cached_state.get("api_lock_state")

    async def turn_on_hazard_lights(self, vehicle_id):
        await self.controller.light_on(vehicle_id)

    async def turn_off_hazard_lights(self, vehicle_id):
        await self.controller.light_off(vehicle_id)

    async def unlock_doors(self, vehicle_id):
        cached_state = self.__get_cached_state(vehicle_id)

        cached_state["assumed_lock_state"] = False
        cached_state["assumed_lock_state_timestamp"] = datetime.datetime.now(datetime.timezone.utc)

        await self.controller.door_unlock(vehicle_id)

    async def lock_doors(self, vehicle_id):
        cached_state = self.__get_cached_state(vehicle_id)

        cached_state["assumed_lock_state"] = True
        cached_state["assumed_lock_state_timestamp"] = datetime.datetime.now(datetime.timezone.utc)

        await self.controller.door_lock(vehicle_id)

    async def start_engine(self, vehicle_id):
        await self.controller.engine_start(vehicle_id)

    async def stop_engine(self, vehicle_id):
        await self.controller.engine_stop(vehicle_id)

    async def send_poi(self, vehicle_id, latitude, longitude, name):
        await self.controller.send_poi(vehicle_id, latitude, longitude, name)

    async def start_charging(self, vehicle_id):
        await self.controller.charge_start(vehicle_id)

    async def stop_charging(self, vehicle_id):
        await self.controller.charge_stop(vehicle_id)

    async def close(self):
        await self.controller.close()

    def __get_cached_state(self, vehicle_id):
        if not vehicle_id in self._cached_state:
            self._cached_state[vehicle_id] = {}

        return self._cached_state[vehicle_id]
