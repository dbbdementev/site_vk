dict = {}




def x(user, token):
    if token in dict:
        list=dict[token]
        list.append(user)
        dict[token]=list
    else:
        list = []
        list.append(user)
        dict[token]=list

    print(dict)




def y(user,token):
    if token in dict:
        dict.pop(token)


    print(dict)



x('1g0', '6666')
x('116', '777777777')
x('1116', '6666')

y('1g0','6666')
