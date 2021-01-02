from pymazda.connection import Connection
from pymazda.exceptions import MazdaException

class Controller:
    def __init__(self, email, password, websession=None):
        self.connection = Connection(email, password, websession)

    async def login(self):
        await self.connection.login()
    
    async def get_tac(self):
        return await self.connection.api_request("GET", "content/getTac/v4", needs_keys=True, needs_auth=False)

    async def get_language_pkg(self):
        postBody = {"platformType": "ANDROID", "region": "MNAO", "version": "2.0.4"}
        return await self.connection.api_request("POST", "junction/getLanguagePkg/v4", body_dict=postBody, needs_keys=True, needs_auth=False)

    async def get_vec_base_infos(self):
        return await self.connection.api_request("POST", "remoteServices/getVecBaseInfos/v4", body_dict={"internaluserid": "__INTERNAL_ID__"}, needs_keys=True, needs_auth=True)

    async def get_vehicle_status(self, internalVin):
        post_body = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin,
            "limit": 1,
            "offset": 0,
            "vecinfotype": "0"
        }
        response = await self.connection.api_request("POST", "remoteServices/getVehicleStatus/v4", body_dict=post_body, needs_keys=True, needs_auth=True)

        if response["resultCode"] != "200S00":
            raise MazdaException("Failed to get vehicle status")

        return response

    async def get_health_report(self, internalVin):
        post_body = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin,
            "limit": 1,
            "offset": 0
        }

        response = await self.connection.api_request("POST", "remoteServices/getHealthReport/v4", body_dict=post_body, needs_keys=True, needs_auth=True)

        if response["resultCode"] != "200S00":
            raise MazdaException("Failed to get health report")

        return response

    async def door_unlock(self, internalVin):
        post_body = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.api_request("POST", "remoteServices/doorUnlock/v4", body_dict=post_body, needs_keys=True, needs_auth=True)

        if response["resultCode"] != "200S00":
            raise MazdaException("Failed to unlock door")

        return response

    async def door_lock(self, internalVin):
        post_body = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.api_request("POST", "remoteServices/doorLock/v4", body_dict=post_body, needs_keys=True, needs_auth=True)

        if response["resultCode"] != "200S00":
            raise MazdaException("Failed to lock door")

        return response

    async def light_on(self, internalVin):
        post_body = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.api_request("POST", "remoteServices/lightOn/v4", body_dict=post_body, needs_keys=True, needs_auth=True)

        if response["resultCode"] != "200S00":
            raise MazdaException("Failed to turn light on")

        return response

    async def light_off(self, internalVin):
        post_body = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.api_request("POST", "remoteServices/lightOff/v4", body_dict=post_body, needs_keys=True, needs_auth=True)

        if response["resultCode"] != "200S00":
            raise MazdaException("Failed to turn light off")

        return response

    async def engine_start(self, internalVin):
        post_body = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.api_request("POST", "remoteServices/engineStart/v4", body_dict=post_body, needs_keys=True, needs_auth=True)

        if response["resultCode"] != "200S00":
            raise MazdaException("Failed to start engine")

        return response

    async def engine_stop(self, internalVin):
        post_body = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.api_request("POST", "remoteServices/engineStop/v4", body_dict=post_body, needs_keys=True, needs_auth=True)

        if response["resultCode"] != "200S00":
            raise MazdaException("Failed to stop engine")

        return response
