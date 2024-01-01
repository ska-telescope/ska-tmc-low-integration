"""This module implement common utils
"""
import json
from os.path import dirname, join


def get_subarray_input_json(slug):
    """
    Args:
        slug (str): base name of file
    Return:
        Read and return content of file
    """
    assign_json_file_path = join(
        dirname(__file__),
        "..",
        "..",
        "..",
        "data",
        "subarray",
        f"{slug}.json",
    )
    with open(assign_json_file_path, "r", encoding="UTF-8") as f:
        assign_json = f.read()
    return assign_json


def get_centralnode_input_json(slug):
    """
    Args:
        slug (str): base name of file
    Return:
        Read and return content of file
    """
    assign_json_file_path = join(
        dirname(__file__),
        "..",
        "..",
        "..",
        "data",
        "centralnode",
        f"{slug}.json",
    )
    with open(assign_json_file_path, "r", encoding="UTF-8") as f:
        assign_json = f.read()
    return assign_json


def update_receptors_in_assignresources_json(
    input_json_str: str, receptors: str
) -> str:
    """
    Update the list of receptors in the given JSON string.

    Args:
        input_json_str (str): Input JSON string containing SDP resources.
        receptor_list (List[str]): List of receptors to replace existing one.

    Returns:
        str: Updated JSON string with the list of receptors modified.

    """
    # Parse the input JSON string
    receptors = receptors.replace('"', "")
    receptors = receptors.split(", ")
    input_json_str = json.loads(input_json_str)

    # Update the list of receptors
    input_json_str["sdp"]["resources"]["receptors"] = receptors

    # Convert the modified JSON back to a string
    input_json_str = json.dumps(input_json_str)

    return input_json_str


class JsonFactory(object):
    """Implement methods required for getting json"""

    def create_subarray_configuration(self, json_type):
        """Read and return configuration json file from
            tests/data/subarray folder
        Args:
            json_type (str): Base name of file which is stored in data folder
        Return:
            config_json (str): Return configure json based json type provided
        """
        return get_subarray_input_json(json_type)

    def create_assign_resources_configuration(self, json_type):
        """Read and return configuration json file from
            tests/data/subarray folder
        Args:
            json_type (str): Base name of file which is stored in data folder
        Return:
            config_json (str): Return configure json based json type provided
        """
        return get_subarray_input_json(json_type)

    def create_centralnode_configuration(self, json_type):
        """Read and return configuration json file from
            tests/data/centralnode folder
        Args:
            json_type (str): Base name of file which is stored in data folder
        Return:
            config_json (str): Return configure json based json type provided
        """
        return get_centralnode_input_json(json_type)
