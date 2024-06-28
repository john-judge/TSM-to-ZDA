library(lme4)
library(merTools)
library(ggplot2)
library(report)
library(sjPlot)

data_file <- 'C:\\Users\\jjudge3\\Desktop\\Data\\mm_full_pipeline_targets\\sagittal\\sagittal_crossing_final_by_pixel.csv'
pixel_df <- read.csv(data_file)
pixel_df

# center Distance and Distance_Along_Barrel_Axis
pixel_df$Distance <- pixel_df$Distance - mean(pixel_df$Distance) 
pixel_df$Distance_Along_Barrel_Axis <- pixel_df$Distance_Along_Barrel_Axis - mean(pixel_df$Distance_Along_Barrel_Axis) 

# Distance_Along_Barrel_Axis is allowed to vary between groups
for (i_barrel in 0:1) {
  print(i_barrel)
  mixed_model = lmer(Value_lat
                     ~ Distance_Along_Barrel_Axis 
                     + Is_Rostral_Crossing
                     + (1 | Litter:Animal:Slice)
                     + (1 | Litter:Animal:Slice:Loc:Barrel)
                     , REML = T,
                     data = pixel_df[pixel_df['Is_Home_Barrel'] == i_barrel, ])
  print(report::report(mixed_model))
}
mixed_model = lmer(Value_lat
                   ~ Distance_Along_Barrel_Axis  + Distance
                   + Is_Rostral_Crossing
                   + (1 | Litter:Animal:Slice)
                   + (1 | Litter:Animal:Slice:Loc:Barrel)
                   , REML = T,
                   data = pixel_df)
print(report::report(mixed_model))


summary(mixed_model)
confint(mixed_model)
ranef(mixed_model)
coef(mixed_model)

predictInterval(mixed_model)   # for various model predictions

REsim(mixed_model)             # mean, median and sd of the random effect estimates

plotREsim(REsim(mixed_model))  # plot the interval estimates.  Intervals that do not include zero are in bold.

ggplot(aes(Distance_Along_Barrel_Axis, Value), data=pixel_df) +
  geom_point()

sjPlot::tab_model(mixed_model)

