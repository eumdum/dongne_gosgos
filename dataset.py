from roboflow import Roboflow
rf = Roboflow(api_key="GduHmcxbyeKZQjHOdTT6")
project = rf.workspace("redbean-bread").project("1_redbeen-bread")
version = project.version(3)
version.model.download("pt")