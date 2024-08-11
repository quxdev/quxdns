import json

import requests

from ..models import Provider


class PorkbunProvider(Provider):
    BASE_URL = "https://porkbun.com/api/json/v3"

    class Meta:
        proxy = True
        verbose_name = "Porkbun"
        verbose_name_plural = "Porkbun"

    @staticmethod
    def headers():
        return {
            "Content-Type": "application/json",
        }

    @staticmethod
    def payload(account, record=None):
        # Basic payload
        if record is None:
            result = {"apikey": account.api_key, "secretapikey": account.secret_api_key}
            return json.dumps(result)

        # Record specific payload
        result = {
            "apikey": account.api_key,
            "secretapikey": account.secret_api_key,
            "name": record.name,
            "type": record.dns_type.name,
            "content": record.value,
            "ttl": record.ttl,
        }
        if record.priority:
            result["prio"] = record.priority
        if record.comment:
            result["note"] = record.comment

        print(result)

        return json.dumps(result)

    @staticmethod
    def _parse_list_records(response, domain):
        records = response["records"]
        data = []
        for record in records:
            ttl = record["ttl"] if "ttl" in record else 600
            ttl = 3600 if int(ttl) > 3600 else ttl

            if "prio" in record:
                if record["prio"] == "0":
                    priority = None
                else:
                    priority = record["prio"]
            else:
                priority = None

            item = {
                "name": record["name"].replace(f".{domain.domain}", ""),
                "dns_type": record["type"].upper(),
                "ttl": ttl,
                "value": record["content"],
                "priority": priority,
                "comment": record["note"] if "note" in record else None,
            }
            data.append(item)

        return data

    def api(self, url, account, record=None):
        headers = self.headers()
        payload = self.payload(account, record)
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            print("404: Page not found")
        else:
            response_dict = response.json()
            print(f"{response.status_code}: {response_dict['message']}")

        return None

    def list_records(self, account=None, domain=None):
        url = f"{self.BASE_URL}/dns/retrieve/{domain.domain}"
        result = self.api(url, account)
        if result is None:
            return None

        result = self._parse_list_records(result, domain)
        return result

    def create_record(self, account=None, domain=None, record=None):
        url = f"{self.BASE_URL}/dns/create/{domain.domain}"
        return self.api(url, account, record)

    def update_record(self, account=None, domain=None, record=None):
        url = (
            f"{self.BASE_URL}/dns/editByNameType/"
            f"{domain.domain}/"
            f"{record.dns_type.name}/"
            f"{record.name}"
        )
        return self.api(url, account, record)

    def delete_record(self, account=None, domain=None, record=None):
        url = (
            f"{self.BASE_URL}/dns/deleteByNameType/"
            f"{domain.domain}/"
            f"{record.dns_type.name}/"
            f"{record.name}"
        )
        return self.api(url, account, record=None)
