library(lme4)
library(merTools)
library(ggplot2)

data_file <- 'C:\\Users\\jjudge3\\Desktop\\Data\\mm_full_pipeline_targets\\sagittal\\sagittal_crossing_final_by_pixel.csv'
pixel_df <- read.csv(data_file)
pixel_df

# Distance_Along_Barrel_Axis is allowed to vary between groups
mixed_model = lmer(Value ~ Distance_Along_Barrel_Axis 
                   + Distance 
                   + Is_Rostral_Crossing
                   + Is_Home_Barrel
                   + (1 | Litter)
                   + (1 | Litter:Animal)
                   + (1 | Litter:Animal:Slice)
                   + (1 | Litter:Animal:Slice:Loc)
                   , data = pixel_df)
summary(mixed_model)
confint(mixed_model)
ranef(mixed_model)$Date
coef(mixed_model)$Date

predictInterval(mixed_model)   # for various model predictions

REsim(mixed_model)             # mean, median and sd of the random effect estimates

plotREsim(REsim(mixed_model))  # plot the interval estimates.  Intervals that do not include zero are in bold.

ggplot(aes(Distance_Along_Barrel_Axis, Value), data=pixel_df)