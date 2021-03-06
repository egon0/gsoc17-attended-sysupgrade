from database import Database
from distutils.version import LooseVersion
import logging
import json

logging.basicConfig(level=logging.DEBUG)

class Request():
    def __init__(self, request_json):
        self.request_json = request_json
        self.response_dict = {}

        # temporary
        self.database = Database()

    def run(self):
        bad_request = self.check_bad_request()
        if bad_request:
            return bad_request

    def check_bad_request(self):
        self.distro_versions = {}
        self.distro_versions["lede"] = ["17.01.1", "17.01.0"]
        self.update_server_url = "http://192.168.1.3:5000"
        if not self.vaild_request():
            logging.info("received invaild update request")
            self.response_dict["error"] = "missing parameters - need %s" % " ".join(self.needed_values)
            return self.respond(), 400

        self.distro = self.request_json["distro"].lower()

        if not self.distro in self.distro_versions:
            logging.info("update request unknown distro")
            self.response_dict["error"] = "unknown distribution %s" % self.distro
            return self.respond(), 400

        self.version = self.request_json["version"]

        if not self.version in self.distro_versions[self.distro]:
            self.response_dict["error"] = "unknown version %s" % self.version
            return self.respond(), 400

        self.target = self.request_json["target"]
        self.subtarget = self.request_json["subtarget"]

        if not self.check_target():
            self.response_dict["error"] = "unknown target %s/%s" % (self.target, self.subtarget)
            return self.respond(), 400

        if "packages" in self.request_json:
            self.packages = self.request_json["packages"]
        #    self.check_packages()
        #    return self.respond(), 200

        return False

    def vaild_request(self):
        # needed params to check sysupgrade
        for value in self.needed_values:
            if not value in self.request_json:
                return False
        return True

    # not sending distro/version. does this change within versions?
    def check_target(self):
        if self.database.check_target(self.target, self.subtarget):
            return True
        return False

    def check_packages(self):
        latest_packages = self.database.check_packages(self.target, self.subtarget, self.packages.keys())

    def init_imagebuilder(self):
        self.imagebuilder = ImageBuilder(self.distro, self.version, self.target, self.subtarget)

    def respond(self):
        logging.debug(self.response_dict)
        return json.dumps(self.response_dict)
   
    # if local version is newer than received returns true
    def version_latest(self, latest, external):
        return LooseVersion(external) >= LooseVersion(latest)
