library(ggplot2)

curr_dir <- getwd()
setwd('/data/sda_output_data/init_exps')
# load the data, ditch the first column, which is epochs numbered from zero
sparse_vs_dense <- read.csv('sparse_vs_dense.csv')

# Faceted plot, 3-params 2 models
full_p <- ggplot(subset(sparse_vs_dense, units = 'relu'), aes(epoch,score, colour = init))
full_p <- full_p + geom_point(alpha = 1/4)
full_p <- full_p + scale_x_discrete(limits = c(0,9))
#full_p <- full_p + scale_y_continuous(limits = c(1000,10000))
full_p <- full_p + facet_grid(arch ~ layer)
full_p <- full_p + stat_smooth()
full_p <- full_p + theme(strip.text.x = element_text(size = 13))
full_p <- full_p + theme(axis.text.x = element_text(size = 13, face = "bold"))
full_p <- full_p + theme(axis.title.x = element_text(size = 13, face = "bold"))
full_p <- full_p + theme(axis.text.y = element_text(size = 13, face = "bold"))
full_p <- full_p + theme(axis.title.y = element_text(size = 13, face = "bold"))
full_p <- full_p + theme(legend.text = element_text(size = 13))
full_p <- full_p + theme(legend.title = element_text(size = 13))
full_p <- full_p + ggtitle("Validation score vs epoch: sparse vs dense initialization")
full_p <- full_p + theme(plot.title = element_text(size=15, face = "bold"))
full_p