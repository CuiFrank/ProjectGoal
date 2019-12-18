from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from goal.models import Goal

# Create your views here.
import django_redis
CACHE = django_redis.get_redis_connection()


def set_goal(request):
    # 返回值
    res_r = {"code": 0, "detail":""}
    res_w = {"code": 1, "detail": ""}
    redis_zset_key = "goal"
    need_store_in_mysql_flag = False

    # 获取参数
    if request.method == 'GET':
        name = request.GET.get('name', '')
        score = request.GET.get('score', '')

        # print("kkkkkkkkkkkk")
        # print(score.isdigit())
        # print("kkkkkkkkkkkk")
        if name and score.isdigit():
            res = res_r
        else:
            res = res_w
            res["detail"] = "参数错误，请检查参数"
            return JsonResponse(res)

        # 查询redis
        res_score = CACHE.zscore(redis_zset_key, name)

        # store redis
        if res_score is None:
            # CACHE.set("test", 1)
            CACHE.zadd(redis_zset_key, {name: int(score)})
            need_store_in_mysql_flag = True
            redis_detail = "no this name , create in redis ..."
        else:
            if int(score) == int(res_score):
                redis_detail = "redis val is equal to now, no need update"
                pass
            else:
                redis_detail = "redis val is not equal to now, need update"
                CACHE.zadd(redis_zset_key, {name: int(score)})
                need_store_in_mysql_flag = True

        # store mysql
        if need_store_in_mysql_flag:
            # 插入mysql
            GoalObj = Goal()
            GoalObj.name = name
            GoalObj.score = score
            GoalObj.save()
            mysql_detail = "store mysql ok"
        else:
            mysql_detail = "no need store mysql"

        # tip 提示信息 # 生产环境去除掉,后期可以改为记录存储日志中
        res['detail'] = "name:{name},score:{score},res_score:{res_score},redis_detail:{redis_detail},mysql_detail:{mysql_detail}".format(
            name=name, score=score, res_score=res_score, redis_detail=redis_detail, mysql_detail=mysql_detail)

    else:
        # todo
        # post 方式暂时先不写
        res = res_w
    return JsonResponse(res)


def get_rank(request):

    # 返回值
    res_r = {"code": 0, "data":"", "detail": ""}
    res_w = {"code": 1, "data": "", "detail": ""}
    redis_zset_key = "goal"

    # 获取参数
    if request.method == 'GET':
        # name 后期可以改为从cookie中获取
        name = request.GET.get('name', '')
        start = request.GET.get('start', '')
        end = request.GET.get('end', '')
        rank_list = []

        if name and start.isdigit() and end.isdigit() and int(start) >= 1 and int(end) >= 1 and int(start) <= int(end):
            # redis中排序是从0开始的，所以进行减一操作
            start = int(start) - 1
            end = int(end) - 1

            # 获取排行
            redis_data = CACHE.zrevrange(redis_zset_key, int(start), int(end),withscores=True)
            res = res_r
            print("************")
            print(redis_data)
            print("************")

            in_redis_flag = 0
            for index,val in enumerate(redis_data):
                # print("------start------")
                # print(val)
                # print(val[0])
                # print(name)
                # print(bytes.decode(val[0]) == name)
                # print("------end------")

                rank_list.append([int(start)+index+1, val[0].decode(), int(val[1])])

                if bytes.decode(val[0]) == name and in_redis_flag == 0:
                    # rank_list.append([int(start)+index+1, name, int(val[1])])
                    in_redis_flag += 1
                    # print("exist .... ")

            # print("-------------")
            # print(rank_list)
            # print("-------------")

            if not in_redis_flag:
                this_rank = CACHE.zrevrank(redis_zset_key, name)
                this_score = CACHE.zscore(redis_zset_key, name)
                if this_rank and this_rank.isdigit():
                    rank_list.append([int(this_rank)+1, name, int(this_score)])

            res["data"] = rank_list

        else:
            res = res_w
            res["detail"] = "参数错误，请检查参数"
    else:
        # todo
        # post 方式暂时先不写
        res = res_w
    return JsonResponse(res)

