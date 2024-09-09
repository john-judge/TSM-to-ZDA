library(lme4)
library(merTools)
library(ggplot2)
library(report)
library(sjPlot)

sag_data_file <- 'C:\\Users\\jjudge3\\Desktop\\Data\\mm_full_pipeline_targets\\sagittal\\sagittal_crossing_final_by_pixel.csv'
sag_df <- read.csv(sag_data_file)
sag_df

cor_data_file <- 'C:\\Users\\jjudge3\\Desktop\\Data\\mm_full_pipeline_targets\\coronal-crossing\\coronal_crossing_final_by_pixel.csv'
cor_df <- read.csv(cor_data_file)
cor_df

all_data_file <- 'C:\\Users\\jjudge3\\Desktop\\Data\\mm_full_pipeline_targets\\coronal-crossing\\coronal_sagittal_crossing_final_by_pixel.csv'
all_df <- read.csv(all_data_file)
all_df

print("What is the effect of sagittal/coronal?")
mixed_model = lmer(Value_lat
                   ~ Distance_Along_Barrel_Axis 
                   + Distance_To_L5
                   + (1 | Litter:Animal:Slice)
                   + (1 | Litter:Animal:Slice:Loc)
                   + (1 | Litter)
                   , REML = T,
                   data = all_df[all_df['Is_Home_Barrel'] == 1, ])
plotREsim(REsim(mixed_model)) 
print(report::report(mixed_model))


for (i_barrel in 0:1) {
  print(i_barrel)
  print("Latency, DABA")
  mixed_model = lmer(Value_lat
                     ~ Distance_Along_Barrel_Axis 
                     + Distance_To_L5
                     + Is_Rostral_Crossing
                     + (1 | Litter:Animal:Slice)
                     + (1 | Litter:Animal:Slice:Loc)
                     , REML = T,
                     data = sag_df[sag_df['Is_Home_Barrel'] == i_barrel, ])
  print(report::report(mixed_model))
  print("Half width, DABA")
  mixed_model = lmer(Value_hw
                     ~ Distance_Along_Barrel_Axis 
                     + Distance_To_L5
                     + Is_Rostral_Crossing
                     + (1 | Litter:Animal:Slice)
                     + (1 | Litter:Animal:Slice:Loc)
                     , REML = T,
                     data = sag_df[sag_df['Is_Home_Barrel'] == i_barrel, ])
  print(report::report(mixed_model))
  print("Amplitude, DABA")
  mixed_model = lmer(Value
                     ~ Distance_Along_Barrel_Axis 
                     + Distance_To_L5
                     + Is_Rostral_Crossing
                     + (1 | Litter:Animal:Slice)
                     + (1 | Litter:Animal:Slice:Loc)
                     , REML = T,
                     data = sag_df[sag_df['Is_Home_Barrel'] == i_barrel, ])
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

