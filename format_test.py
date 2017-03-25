args = ['hello']*3
print args
print tuple(args)
print '{:<30}{:^30}{:>30}'.format(*args)
