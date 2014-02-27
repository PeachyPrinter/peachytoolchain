import os

from audio.tuning_parameter_file import TuningParameterFileHandler

class CureRateCalibrator(object):
    
    def __init__(self, calibration_file):
        self.calibration_data = self.load_calibration(calibration_file)

    def load_calibration(self,calibration_file):
        if (not os.path.exists(calibration_file)):
            raise Exception("Calibration File %s does not exist at the specified location" % calibration_file)
        return TuningParameterFileHandler.read_from_file(calibration_file)

    def start(self):
        #write a base 2mm
        #
        #print solid for 1 mm and record max sublayers
        #print next 1mm skipping every 10th sublayer
        #print next 1mm skipping every 9th sublayer
        #print next 1mm skipping every 8th sublayers...
        pass
