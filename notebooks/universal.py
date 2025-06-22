import matplotlib as mpl

# color dictionary for experiments
experiments = ['piControl','deepmip_sens_1xCO2','deepmip_stand_3xCO2','deepmip_stand_6xCO2','deepmip_sens_9xCO2']
colors = {e:c for e,c in zip(experiments,mpl.colors.TABLEAU_COLORS.keys())}