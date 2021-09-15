# Copyright 2020 - 2021 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from monai.deploy.core import Application
from monai.deploy.operators.dicom_data_loader_operator import DICOMDataLoaderOperator
from monai.deploy.operators.dicom_series_selector_operator import DICOMSeriesSelectorOperator
from monai.deploy.operators.dicom_series_to_volume_operator import DICOMSeriesToVolumeOperator
from monai.deploy.operators.png_converter_operator import PNGConverterOperator


class App(Application):
    def compose(self):
        study_loader_op = DICOMDataLoaderOperator()
        series_selector_op = DICOMSeriesSelectorOperator()
        series_to_vol_op = DICOMSeriesToVolumeOperator()
        png_converter_op = PNGConverterOperator()

        self.add_flow(study_loader_op, series_selector_op, {"dicom_study_list": "dicom_study_list"})
        self.add_flow(series_selector_op, series_to_vol_op, {"dicom_series": "dicom_series"})
        self.add_flow(series_to_vol_op, png_converter_op, {"image": "image"})


if __name__ == "__main__":
    App(do_run=True)
