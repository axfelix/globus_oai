from harvester.HarvestRepository import HarvestRepository
import requests
import time
import json
import re
import os.path


class OpenDataSoftRepository(HarvestRepository):
    """ OpenDataSoft Repository """

    def setRepoParams(self, repoParams):
        self.metadataprefix = "opendatasoft"
        super(OpenDataSoftRepository, self).setRepoParams(repoParams)
        self.domain_metadata = []
        self.records_per_request = 50
        self.params = {
            "start": 0,
            "pageLength": self.records_per_request
        }
        self.query = "((*))"
        if "collection" in repoParams:
            coll = re.sub("[^a-zA-Z0-9_-]+", "", repoParams["collection"])  # Remove potentially bad chars
            self.query += "%2520AND%2520(coll:" + coll + ")"
        if "options" in repoParams:
            options = re.sub("[^a-zA-Z0-9_-]+", "", repoParams["options"])  # Remove potentially bad chars
            self.params["options"] = options

    def _crawl(self):
        kwargs = {
            "repo_id": self.repository_id, "repo_url": self.url, "repo_set": self.set, "repo_name": self.name,
            "repo_type": "opendatasoft",
            "enabled": self.enabled, "repo_thumbnail": self.thumbnail, "item_url_pattern": self.item_url_pattern,
            "abort_after_numerrors": self.abort_after_numerrors,
            "max_records_updated_per_run": self.max_records_updated_per_run,
            "update_log_after_numitems": self.update_log_after_numitems,
            "record_refresh_days": self.record_refresh_days,
            "repo_refresh_days": self.repo_refresh_days, "homepage_url": self.homepage_url,
            "repo_oai_name": self.repo_oai_name
        }
        self.repository_id = self.db.update_repo(**kwargs)

        try:
            offset = 0
            while True:
                self.params["start"] = offset
                payload = {"rows": self.records_per_request, "start": self.params["start"]}
                response = requests.get(self.url, params=payload,
                                        verify=False)  # Needs to be string not dict to force specific urlencoding
                records = response.json()
                if not records["datasets"]:
                    break
                for record in records["datasets"]:
                    oai_record = self.format_opendatasoft_to_oai(record)
                    if oai_record:
                        self.db.write_record(oai_record, self)
                offset += self.records_per_request

            return True

        except Exception as e:
            self.logger.error("Updating OpenDataSoft Repository failed: {}".format(e))
            self.error_count = self.error_count + 1
            if self.error_count < self.abort_after_numerrors:
                return True

        return False

    def format_opendatasoft_to_oai(self, opendatasoft_record):
        record = {}
        print(opendatasoft_record)
        record["identifier"] = opendatasoft_record["datasetid"]
        record["creator"] = opendatasoft_record["metas"]["data-owner"]
        record["pub_date"] = opendatasoft_record["metas"]["modified"]
        try:
            record["tags"] = opendatasoft_record["metas"]["keyword"]
        except:
            record["tags"] = []
        try:
            record["subject"] = opendatasoft_record["metas"]["theme"]
        except:
            pass
        record["title"] = opendatasoft_record["metas"]["title"]
        try:
            record["rights"] = opendatasoft_record["metas"]["license"]
        except:
            pass
        record["description"] = opendatasoft_record["metas"]["description"]
        record["publisher"] = opendatasoft_record["metas"]["publisher"]
        try:
            record["affiliation"] = opendatasoft_record["metas"]["data-team"]
        except:
            pass
        record["series"] = ""
        record["title_fr"] = ""

        return record

    def _update_record(self, record):
        # There is no update for individual records, they are updated on full crawl
        return True
