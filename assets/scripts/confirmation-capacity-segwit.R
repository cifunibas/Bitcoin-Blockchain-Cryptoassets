rm(list=ls())

# library
library(zoo)
library(ggplot2)
library(here)

WorkDir <- here("Documents", "GitHub", "Bitcoin-Blockchain-Cryptoassets")
setwd(WorkDir)

beta <- seq(0, 1, 1/1000)
C <- 4 / (3*(1-beta) + 1)

data <- data.frame(beta = beta, C = C)
ggplot(data = data, aes(x = beta, y = C)) +
  geom_line() +
  theme_bw() +
  labs(x = expression("Fraction of witness data "*beta), y = "Confirmation capacity in MB") +
  scale_y_continuous(breaks = c(0, 1, 2, 3, 4)) +
  scale_x_continuous(breaks = c(0.0, 0.2, 0.4, 0.6, 0.8, 1.0))
ggsave("assets/figures/confirmation-capacity-segwit.pdf", width = 8, height = 4.5)