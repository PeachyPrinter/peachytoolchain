
class CureRateCalibrator(object):

    def __init__(self,drip_detector,drips_per_mm):
        if(drips_per_mm <= 0.0):
            raise Exception("drips_per_mm must be a positive number greater then 0 was: %s" % drips_per_mm)
        self._drip_detector = drip_detector
        self._drips_per_mm = drips_per_mm

    def current_height_mm(self):
        return self._drip_detector.num_drips / self._drips_per_mm

    def start(self):
        #write a base 2mm
        #
        #print solid for 1 mm and record max sublayers
        #print next 1mm skipping every 10th sublayer
        #print next 1mm skipping every 9th sublayer
        #print next 1mm skipping every 8th sublayers...


        pass
