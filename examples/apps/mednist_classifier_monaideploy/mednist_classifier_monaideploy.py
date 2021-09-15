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

from monai.deploy.core import (
    Application,
    DataPath,
    ExecutionContext,
    Image,
    InputContext,
    IOType,
    Operator,
    OutputContext,
    env,
    input,
    output,
    resource,
)
from monai.transforms import AddChannel, Compose, EnsureType, ScaleIntensity

MEDNIST_CLASSES = ["AbdomenCT", "BreastMRI", "CXR", "ChestCT", "Hand", "HeadCT"]


@input("image", DataPath, IOType.DISK)
@output("image", Image, IOType.IN_MEMORY)
@env(pip_packages=["pillow"])
class LoadPILOperator(Operator):
    """Load image from the given input (DataPath) and set numpy array to the output (Image)."""

    def compute(self, input: InputContext, output: OutputContext, context: ExecutionContext):
        import numpy as np
        from PIL import Image as PILImage

        input_path = input.get().path

        image = PILImage.open(input_path)
        image = image.convert("L")  # convert to greyscale image
        image_arr = np.asarray(image)

        output_image = Image(image_arr)  # create Image domain object with a numpy array
        output.set(output_image)


@input("image", Image, IOType.IN_MEMORY)
@output("output", DataPath, IOType.DISK)
@env(pip_packages=["monai"])
class MedNISTClassifierOperator(Operator):
    """Classifies the given image and returns the class name."""

    @property
    def transform(self):
        return Compose([AddChannel(), ScaleIntensity(), EnsureType()])

    def compute(self, input: InputContext, output: OutputContext, context: ExecutionContext):
        import json

        import torch

        img = input.get().asnumpy()  # (64, 64), uint8
        image_tensor = self.transform(img)  # (1, 64, 64), torch.float64
        image_tensor = image_tensor[None].float()  # (1, 1, 64, 64), torch.float32

        # Comment below line if you want to do CPU inference
        image_tensor = image_tensor.cuda()

        model = context.models.get()  # get a TorchScriptModel object
        # Uncomment the following line if you want to do CPU inference
        # model.predictor = torch.jit.load(model.path, map_location="cpu").eval()

        with torch.no_grad():
            outputs = model(image_tensor)

        _, output_classes = outputs.max(dim=1)

        result = MEDNIST_CLASSES[output_classes[0]]  # get the class name
        print(result)

        # Get output (folder) path and create the folder if not exists
        output_folder = output.get().path
        output_folder.mkdir(parents=True, exist_ok=True)

        # Write result to "output.json"
        output_path = output_folder / "output.json"
        with open(output_path, "w") as fp:
            json.dump(result, fp)


@resource(cpu=1, memory="1Gi")
class App(Application):
    """Application class for the MedNIST classifier."""

    def compose(self):
        load_pil_op = LoadPILOperator()
        classifier_op = MedNISTClassifierOperator()

        self.add_flow(load_pil_op, classifier_op)


if __name__ == "__main__":
    App(do_run=True)
