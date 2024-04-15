import pstats
p = pstats.Stats('profile_output')
p.sort_stats('cumulative').print_stats(10)  # Adjust the number to control how many entries to show
