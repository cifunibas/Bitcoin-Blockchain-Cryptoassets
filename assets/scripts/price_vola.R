rm(list=ls())

# library
library(zoo)
library(ggplot2)
library(here)

WorkDir <- here("Documents", "GitHub", "Bitcoin-Blockchain-Cryptoassets")
setwd(WorkDir)

# data: load data and create ts of P, p, R and r
btcusd <- read.csv("assets/data/btc_prices.csv") # coindesk data
inds <- as.Date(substring(btcusd$Date, 1, 8), format = "%d.%m.%y")
larger_than_zero <- btcusd$BTCUSD > 0
P <- zoo(as.numeric(btcusd$BTCUSD[larger_than_zero]), inds[larger_than_zero])
p <- log(P)
r <- diff(log(P))
R <- exp(r) - 1
data <- merge(P, p, R, r)

# graph: price
P_graph <- autoplot(data$P) + theme_bw() + labs(x = "Time", y = "Bitcoin Price (USD)") + scale_y_continuous(breaks = c(2*10^4, 4*10^4, 6*10^4, 8*10^4), labels = c("20,000", "40,000", "60,000", "80,000"))
P_graph
ggsave("assets/figures/price_graph.pdf", width = 8, height = 4.5)

# graph: log-price
p_graph <- autoplot(data$p) + theme_bw() + labs(x = "Time", y = "Bitcoin Price (USD, log-scale)") + scale_y_continuous(breaks = c(log(1), log(10), log(100), log(1000), log(10000), log(100000)), labels = c("1", "10", "100", "1,000", "10,000", "100,000"))
p_graph
ggsave("assets/figures/log_price_graph.pdf", width = 8, height = 4.5)

# graph: log-price incl. halvings
halving_dates <- as.Date(c("2012-11-29", "2016-07-10", "2020-05-11"))
halving_p <- p[halving_dates]
halvings <- data.frame(dates = halving_dates, p = halving_p, row.names = NULL)
p_graph_halvings <- p_graph + geom_area(halvings, mapping = aes(x = ifelse(x >= dates & x < dates + 366, x, 0), y = p), colour = "grey")
p_graph_halvings
ggsave("assets/figures/log_price_halvings_graph.pdf", width = 8, height = 4.5)

# graph: returns
R_graph <- autoplot(data$R) + theme_bw() + labs(x = "Time", y = "Returns (daily)")
R_graph
ggsave("assets/figures/returns.pdf", width = 8, height = 4.5)

# graph: log-returns
r_graph <- autoplot(data$r) + theme_bw() + labs(x = "Time", y = "Log-returns (daily)")
r_graph
ggsave("assets/figures/log_returns.pdf", width = 8, height = 4.5)

# graph: 1-year rolling volatility
rolling_interval <- 365
year <- 365
rolling_vola <- rollapply(data$R, rolling_interval, align = "right", function(x) sd(x))
ann_rolling_vola <- sqrt(year) * rolling_vola
volatility_graph <- autoplot(ann_rolling_vola) + theme_bw() + labs(x = "Time", y = "Annualized volatility of daily returns (over the last 365 days)") + scale_y_continuous(breaks = c(0, 1, 2, 3), labels = c("0", "100%", "200%", "300%"))
volatility_graph
ggsave("assets/figures/volatility.pdf", width = 8, height = 4.5)

# load data and create ts of actual Bitcoin supply and actual growth rate of Bitcoin units
actual_bitcoins <- read.csv("assets/data/total_bitcoins.csv")
inds2 <- as.Date(substr(actual_bitcoins$Timestamp, 1, 10))
duplicated_dates <- which(duplicated(inds2))
inds2 <- inds2[-duplicated_dates]
mined_btc <- zoo(as.numeric(actual_bitcoins$total.bitcoins), inds2)

# graph: mined bitcoin units
mined_btc_graph <- autoplot(mined_btc) + theme_bw() + labs(x = "Time", y = "Number of Bitcoin units") + scale_y_continuous(breaks = c(0, 0.5*10^7, 10^7, 1.5*10^7, 2*10^7), labels = c("0", "5M", "10M", "15M", "20M"))
mined_btc_graph
ggsave("assets/figures/mined_btc.pdf", width = 8, height = 4.5)

# approximate theoretical number of bitcoin units
blocks_per_day <- 24*60/10
halving_after <- 210000
block_reward <- c(50, 25, 12.5, 6.25)
theoretical_new_btc <- c(rep(blocks_per_day*block_reward[1], floor(halving_after/blocks_per_day)), rep(blocks_per_day*block_reward[2], floor(halving_after/blocks_per_day)), rep(blocks_per_day*block_reward[3], floor(halving_after/blocks_per_day)), rep(blocks_per_day*block_reward[4], floor(halving_after/blocks_per_day)))
theoretical_total_btc <- cumsum(theoretical_new_btc)
first_data_point <- inds2[1]
last_data_point <- inds2[length(inds2)]
duration <- seq(as.Date(first_data_point), as.Date(last_data_point), 1)
theoretical_btc <- zoo(theoretical_total_btc[1:length(duration)], duration)[inds2]

# graph: theoretical bitcoin units
theoretical_btc_graph <- autoplot(theoretical_btc) + theme_bw() + labs(x = "Time", y = "Number of Bitcoin units") + scale_y_continuous(breaks = c(0, 0.5*10^7, 10^7, 1.5*10^7, 2*10^7), labels = c("0", "5M", "10M", "15M", "20M"))
theoretical_btc_graph
ggsave("assets/figures/theoretical_btc.pdf", width = 8, height = 4.5)

# graph: mined vs. theoretical bitcoin units
mined_theoretical <- merge(mined_btc, theoretical_btc)
mined_theoretical_graph <- autoplot(mined_theoretical, facets = NULL) +
  theme_bw() +
  theme(legend.justification = c(0, 1),
        legend.position = c(0, 1),
        legend.title = element_blank(),
        legend.box.background = element_rect(colour = "black")) +
  scale_colour_manual(breaks = c("mined_btc", "theoretical_btc"), 
                       labels = c("Actual path", "Theoretical path"),
                       values = c("black", "grey")) +
  labs(x = "Time",
       y = "Number of Bitcoin units in millions") +
  scale_y_continuous(breaks = c(0, 0.5*10^7, 10^7, 1.5*10^7, 2*10^7), labels = c("0", "5M", "10M", "15M", "20M"))
mined_theoretical_graph
ggsave("assets/figures/mined_theoretical_btc.pdf", width = 8, height = 4.5)

# data: get final data point for each month and calculate monthly growth rate
btc_eom <- subset(mined_theoretical, !duplicated(as.yearmon(index(mined_theoretical), "%Y%m"), fromLast = TRUE))
gr_btc <- diff(btc_eom$mined_btc) / btc_eom$mined_btc

# graph: bitcoin supply growth
btc_growth_graph <- autoplot(gr_btc) + theme_bw() + labs(x = "Time", y = "Growth rate of the monetary base (BTC, per month)") + scale_y_continuous(breaks = c(0, 0.2, 0.4, 0.6), labels = c("0", "20%", "40%", "60%"))
btc_growth_graph
ggsave("assets/figures/btc_growth.pdf", width = 8, height = 4.5)

# data: load US dollar monetary base data (monthly)
usd <- read.csv("assets/data/usd_monetary_base.csv")
usd_eom <- zoo(usd$BOGMBASE, as.Date(usd$DATE))
gr_usd <- diff(usd_eom) / usd_eom

# graph: usd supply growth
usd_growth_graph <- autoplot(gr_usd) + theme_bw() + labs(x = "Time", y = "Growth rate of monetary base (USD,  per month)")
usd_growth_graph
ggsave("assets/figures/usd_growth.pdf", width = 8, height = 4.5)

# graph: btc supply growth vs. usd supply growth
gr_btc2 <- zoo(gr_btc[2:(length(gr_btc))], index(gr_usd))
gr_btc_usd <- merge(gr_btc2, gr_usd)
gr_btc_usd_graph <- autoplot(gr_btc_usd, facet = NULL) +
  theme_bw() +
  theme(legend.justification = c(1, 1),
        legend.position = c(1, 1),
        legend.title = element_blank(),
        legend.box.background = element_rect(colour = "black")) +
  scale_colour_manual(breaks = c("gr_btc2", "gr_usd"), 
                      labels = c("BTC", "USD"),
                      values = c("black", "grey")) +
  labs(x = "Time", y = "Growth rate of monetary base (per month)") +
  ylim(-0.1, 0.4) +
  scale_y_continuous(breaks = c(-0.05, 0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4),
                     labels = c("-5%", "0%", "5%", "10%", "15%", "20%", "25%", "30%", "35%", "40%"))
gr_btc_usd_graph
ggsave("assets/figures/btc_usd_growth.pdf", width = 8, height = 4.5)
