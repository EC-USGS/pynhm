import pathlib

import yaml
from yaml import Loader


def pytest_addoption(parser):
    parser.addoption(
        "--domain_yaml",
        required=False,
        action="append",
        default=[],
        help=(
            "YAML file(s) for indiv domain tests "
            "(can pass multiples of this argument)"
        ),
    )


def pytest_generate_tests(metafunc):
    if "domain" in metafunc.fixturenames:
        domain_file_list = metafunc.config.getoption("domain_yaml")
        if len(domain_file_list) == 0:
            domain_file_list = ["../test_data/drb_2yr/drb_2yr.yaml"]

        # open and read in the yaml and
        domain_ids = [pathlib.Path(ff).stem for ff in domain_file_list]
        domain_list = []
        for dd in domain_file_list:
            dd_file = pathlib.Path(dd)
            with dd_file.open("r") as yaml_file:
                domain_dict = yaml.safe_load(yaml_file)
                # Construct/derive some convenience quantities
                domain_dict["file"] = dd_file
                domain_dict["dir"] = dd_file.parent
                # Transform all relative paths in the yaml (relative to the yaml file)
                # using the rel path to the file - spare the tester from doing this.
                domain_dict["param_file"] = pathlib.Path(
                    domain_dict["param_file"]
                )
                if not domain_dict["param_file"].is_absolute():
                    domain_dict["param_file"] = (
                        domain_dict["dir"] / domain_dict["param_file"]
                    )
                for fd_key in ["prms_outputs", "cbh_inputs"]:
                    domain_dict[fd_key] = {
                        key: pathlib.Path(val)
                        for key, val in domain_dict[fd_key].items()
                    }
                    domain_dict[fd_key] = {
                        key: domain_dict["dir"] / val
                        for key, val in domain_dict[fd_key].items()
                        if not pathlib.Path(val).is_absolute()
                    }
                # Construct a dictonary that gets used in CBH
                domain_dict["input_files_dict"] = {
                    key: val for key, val in domain_dict["cbh_inputs"].items()
                }
                # append to the list of all domains
                domain_list += [domain_dict]

        metafunc.parametrize("domain", domain_list, ids=domain_ids)