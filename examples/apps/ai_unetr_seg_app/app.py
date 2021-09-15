# Copyright 2021 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from unetr_seg_operator import UnetrSegOperator

from monai.deploy.core import Application, resource
from monai.deploy.operators.dicom_data_loader_operator import DICOMDataLoaderOperator
from monai.deploy.operators.dicom_seg_writer_operator import DICOMSegmentationWriterOperator
from monai.deploy.operators.dicom_series_selector_operator import DICOMSeriesSelectorOperator
from monai.deploy.operators.dicom_series_to_volume_operator import DICOMSeriesToVolumeOperator


@resource(cpu=1, gpu=1, memory="7Gi")
# pip_packages can be a string that is a path(str) to requirements.txt file or a list of packages.
# The MONAI pkg is not required by this class, instead by the included operators.
class AIUnetrSegApp(Application):
    def __init__(self, *args, **kwargs):
        """Creates an application instance."""

        self._logger = logging.getLogger("{}.{}".format(__name__, type(self).__name__))
        super().__init__(*args, **kwargs)

    def run(self):
        # This method calls the base class to run. Can be omitted if simply calling through.
        self._logger.debug(f"Begin {self.run.__name__}")
        super().run()
        self._logger.debug(f"End {self.run.__name__}")

    def compose(self):
        """Creates the app specific operators and chain them up in the processing DAG."""

        self._logger.debug(f"Begin {self.compose.__name__}")
        # Creates the custom operator(s) as well as SDK built-in operator(s).
        study_loader_op = DICOMDataLoaderOperator()
        series_selector_op = DICOMSeriesSelectorOperator()
        series_to_vol_op = DICOMSeriesToVolumeOperator()
        # Model specific inference operator, supporting MONAI transforms.
        unetr_seg_op = UnetrSegOperator()
        # Creates DICOM Seg writer with segment label name in a string list
        dicom_seg_writer = DICOMSegmentationWriterOperator(
            seg_labels=[
                "spleen",
                "rkid",
                "lkid",
                "gall",
                "eso",
                "liver",
                "sto",
                "aorta",
                "IVC",
                "veins",
                "pancreas",
                "rad",
                "lad",
            ]
        )

        # Create the processing pipeline, by specifying the upstream and downstream operators, and
        # ensuring the output from the former matches the input of the latter, in both name and type.
        self.add_flow(study_loader_op, series_selector_op, {"dicom_study_list": "dicom_study_list"})
        self.add_flow(series_selector_op, series_to_vol_op, {"dicom_series": "dicom_series"})
        self.add_flow(series_to_vol_op, unetr_seg_op, {"image": "image"})
        # Note below the dicom_seg_writer requires two inputs, each coming from a upstream operator.
        self.add_flow(series_selector_op, dicom_seg_writer, {"dicom_series": "dicom_series"})
        self.add_flow(unetr_seg_op, dicom_seg_writer, {"seg_image": "seg_image"})

        self._logger.debug(f"End {self.compose.__name__}")


if __name__ == "__main__":
    # Creates the app and test it standalone. When running is this mode, please note the following:
    #     -m <model file>, for model file path
    #     -i <DICOM folder>, for input DICOM CT series folder
    #     -o <output folder>, for the output folder, default $PWD/output
    # e.g.
    #     python3 app.py -i input -m model/model.ts
    #
    logging.basicConfig(level=logging.DEBUG)
    app_instance = AIUnetrSegApp()  # Optional params' defaults are fine.
    app_instance.run()
