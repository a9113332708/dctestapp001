# Work with Python 3.6
import discord
import os
import discord
import random
import re
from datetime import datetime as dt, timedelta
import pickle
# from dotenv import load_dotenv

# load_dotenv()
# token = os.getenv(TOKEN)

DISCORD_TOKEN = "Nzk2OTM5MDAzNjUxMTYyMTIz.X_fNSA.nfTZec1Ng08Bw1tOew56CtDe1mc"
QUEUE_GUILD = 566405949137616936
#DISCORD_MANAGE_ROLE = 
queue_channel = 800569452767871006


TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('QUEUE_GUILD')
client = discord.Client()

"""
    print (message.author)
    print (message.channel.id)
    print (message.author.name)
    print (message.author.id)    
    print (message.author.display_name)     
    print (message.content[:3])  
    .mention
"""
admin_role = 682886327976460319
guild_member_map = {}
global_user = 796117413536071685

@client.event
async def on_ready():
    for g in client.guilds:
        if g.id == QUEUE_GUILD:
            guild = g
            break
    global admin_role
    global guild_member_map
    global global_user
    for role in guild.roles:
        print(role.name, role.id)
        if role.name == "administration":
            admin_role = role
    for member in guild.members:
        display_name = member.display_name
        if display_name == '深夜積分戰場頻道成員':
            global_user = member
        if display_name not in guild_member_map:
            guild_member_map[display_name] = member      
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
        f'{admin_role.name}(id: {admin_role.id})'
    )
quing = []
land_quing = []
qued_user = []
stop_quing = False

def split_by_space(row):
    data = row.split(' ')
    while '' in data:
        data.remove('')
    return data
def signuperror(user):
    return '%s 報名格式為 !報名 LM|BL 角色名稱' % user.mention

def respon_q_list(quing):
    global qued_user
    respon_str = '!隊伍列表\n'
    respon_str += '```聯盟 : \n'
    counter = 1
    for camp, character_name, quing_user in quing:
        if quing_user not in qued_user:
            qued_user.append(quing_user)
        if camp != 'LM':
            continue
        respon_str += '%.2d. %s (%s) \n' % (counter, character_name, quing_user.display_name) 
        counter += 1
    
    respon_str += '\n部落 : \n'        
    counter = 1
    for camp, character_name, quing_user in quing:
        if quing_user not in qued_user:
            qued_user.append(quing_user)
        if camp != 'BL':
            continue
        respon_str += '%.2d. %s (%s) \n' % (counter, character_name, quing_user.display_name) 
        counter += 1
    return respon_str + '```'

def check_queue(user, row, quing):
    data = split_by_space(row)
    if len(data) < 3:
        return signuperror(user)
    if data[1] == '聯盟':
        camp = 'LM'
    elif data[1] == '部落':
        camp = 'BL'
    else:
        camp = data[1].upper()
    if camp not in ['LM', 'BL']:
        return signuperror(user)
    character_name = data[2]
    discord_name = user.display_name

    # for camp_q, character_name_q, quing_user in quing:
    #     if quing_user == user:
    #         return user.mention + '已在列隊中，請勿重複報名'
    quing.append((camp, character_name, user))
    return '%s 已報名成功 \n' % user.mention + respon_q_list(quing)

def Agent_check_queue(user_o, user, row, quing):
    data = split_by_space(row)
    if len(data) < 4:
        return signuperror(user)
    if data[2] == '聯盟':
        camp = 'LM'
    elif data[2] == '部落':
        camp = 'BL'
    else:
        camp = data[2].upper()
    if camp not in ['LM', 'BL']:
        return signuperror(user)
    character_name = data[3]
    discord_name = user.display_name
    for camp_q, character_name_q, quing_user in quing:
        if quing_user == user:
            return user.mention + '已在列隊中，請勿重複報名'
    quing.append((camp, character_name, user))
    return '%s 代 %s 報名成功 \n' % (user_o.mention, user.mention) + respon_q_list(quing)    

def cancel_queue(user, row, quing):
    global qued_user    
    result = ''
    data = split_by_space(row)
    character_name_list = []
    if len(data) > 1:
        if ',' in data[1]:
            character_name_list = data[1].split(',')
        else:
            character_name_list = data[1].split('，')
            
    remove_list = []
    for camp_q, character_name_q, quing_user in quing:
        if quing_user == user:
            if len(character_name_list) == 0 or character_name_q in character_name_list:
                remove_list.append((camp_q, character_name_q, user))
    for remove_u in remove_list:
        quing.remove(remove_u)
        result += '%s(%s)' % (remove_u[1], user.display_name) + ' 已成功取消報名 \n'
        if remove_u[2] in qued_user:
            qued_user.remove(remove_u[2])
    if result == '':
        return user.mention + '不再列隊中'
    return result + respon_q_list(quing)

def quit_queue(user, row, quing):
    result = ''
    data = split_by_space(row)
    character_name_list = []
    if len(data) > 1:
        if ',' in data[1]:
            character_name_list = data[1].split(',')
        else:
            character_name_list = data[1].split('，')
    remove_list = []
    for camp_q, character_name_q, quing_user in quing:
        if quing_user == user:
            if len(character_name_list) == 0 or character_name_q in character_name_list:
                remove_list.append((camp_q, character_name_q, user))
    for remove_u in remove_list:
        quing.remove(remove_u)
        result += '%s(%s) 已進組，從列隊中移除\n' % (remove_u[1], user.display_name)
    if result == '':
        return user.mention + '不再列隊中'
    return result + respon_q_list(quing)

def requeue(user, row, quing):
    data = split_by_space(row)
    if len(data) < 3:
        return "指令錯誤 正確格式為: \n!清除隊伍 LM|BL ?|ALL(可指定清除前幾人或用ALL全清)\n"
    camp = data[1]
    if camp not in ['LM', 'BL', '聯盟', '部落']:
        return "指令錯誤 正確格式為: \n!清除隊伍 LM|BL ?|ALL(可指定清除前幾人或用ALL全清)\n"
    number = data[2]
    try:
        if number == 'ALL':
            number = 999
        else:
            number = int(number)
    except:
        return "指令錯誤 正確格式為: \n!清除隊伍 LM|BL ?|ALL(可指定清除前幾人或用ALL全清)\n"
    if camp == '聯盟':
        camp = 'LM'
    if camp == '部落':
        camp = 'BL'
    count = number
    remove_user = []
    remove_list = []
    for camp_q, character_name_q, quing_user in quing:
        if count == 0:
            break
        if camp_q == camp:
            count = count - 1
            remove_list.append((camp_q, character_name_q, quing_user))
            if quing_user == None:
                remove_user.append(character_name_q)
            else:
                remove_user.append(quing_user)
    for remove_u in remove_list:
        quing.remove(remove_u)
    result = ""
    for r_user in set(remove_user):
        try:
            mention = r_user.mention
        except:
            mention = r_user
        result += mention + " "
    result += "\n 已從列隊中移除\n"
    return result  + respon_q_list(quing)

def rmqueue(user, quing):
    global qued_user
    for camp_q, character_name_q, quing_user in quing:
        if quing_user in qued_user:
            qued_user.remove(quing_user)
    quing.clear()
    return user.mention + ' 列隊已完全清空，請所有人重新報名\n'


def set_queue(user, rows, quing):
    global guild_member_map
    global global_user
    regex = re.compile(r'(\d*).\s(.*)\s[(]+(.*)[)]+')
    lines = rows.split('\n')
    camp = None
    for row in lines:
        if '聯盟' in row:
            camp = 'LM'
            continue
        elif '部落' in row:
            camp = 'BL'
            continue
        m = regex.match(row)
        if m is None:
            continue
        character_name_q = m.group(2)
        display_name_q = m.group(3)
        if display_name_q not in guild_member_map.keys():
            user_q = global_user
        else:
            user_q = guild_member_map[display_name_q]
        quing.append((camp, character_name_q, user_q))
    return user.mention + '列表已經登入完成\n'

# def admin_cancel_queue(user_list, row):
#     global quing
#     data = split_by_space(row)
#     print (data)
#     if len(data) != 2:
#         return '代取消報名格式為 !代取消報名 成員(tag, 可一次多個)'
#     result = ''
#     print (user_list)
#     for camp_q, character_name_q, quing_user in quing:
#         print (quing_user)
#         if quing_user in user_list:
#             quing.remove((camp_q, character_name_q, quing_user))
#             result += user.mention + '已成功取消 %s 的報名 \n' % quing_user.mention
#     if result != '':
#         return result + respon_q_list(quing)
#     return '指定取消對象不再列隊中 \n'

def admin_cancel_queue(row, quing):
    data = split_by_space(row)
    if len(data) != 2:
        return '移除列隊格式為 !移除列隊 角色名稱(可一次多個 用,分開)'
    if ',' in data[1]:
        character_name_list = data[1].split(',')
    else:
        character_name_list = data[1].split('，')
    result = ''
    remove_list = []
    for camp_q, character_name_q, quing_user in quing:
        if character_name_q in character_name_list:
            remove_list.append((camp_q, character_name_q, quing_user))

    for remove_u in remove_list:
        quing.remove(remove_u)
        result += '已成功取消 %s 的報名 \n' % remove_u[1]
    if result != '':
        return result + respon_q_list(quing)
    return '指定取消對象不再列隊中 \n'

def admin_cancel_queue_number(row, quing):
    data = split_by_space(row)
    if len(data) != 3:
        return '移除列隊格式為 !移除編號 LM|BL ?(可指定清除編號?的人)\n'
    camp = data[1]
    if camp not in ['LM', 'BL', '聯盟', '部落']:
        return "移除列隊格式為 !移除編號 LM|BL ?(可指定清除編號?的人)\n"
    if ',' in data[2]:
        number_list = data[2].split(',')
    else:
        number_list = data[2].split('，')
    number_list_int = []
    for number in number_list:
        try:
            number_list_int.append(int(number))
        except:
            return '移除列隊格式為 !移除編號 LM|BL ?(可指定清除編號?的人)\n'
    if camp == '聯盟':
        camp = 'LM'
    if camp == '部落':
        camp = 'BL'
    result = ''
    count = 0
    remove_list = []
    for camp_q, character_name_q, quing_user in quing:
        if camp_q == camp:
            count += 1
        if camp_q == camp and count in number_list_int:
            remove_list.append((camp_q, character_name_q, quing_user))
    for remove_u in remove_list:
        quing.remove(remove_u)
        result += '已成功取消 %s 的報名 \n' % remove_u[1]
    if result != '':
        return result + respon_q_list(quing)
    return '指定取消編號不存在 \n'

def cmd_list():
    string = "```!列表\n"
    string += "!報名 LM|BL 角色名稱\n"
    string += "!取消報名 角色名稱(可一次多個，用,分開，不填就是全部取消)\n"
    #string += "!進組 角色名稱(可一次多個，用,分開，不填就是全部取消)\n"        
    string += "(管理員限定)\n"
    string += "!移除列隊 角色名稱(可一次多個 用,分開)'\n"
    string += "!移除編號 LM|BL ?(可指定清除編號?的人，可一次多個 用,分開)\n"
    string += "!清除隊伍 LM|BL ?|ALL(可指定清除前幾人或用ALL全清)\n"
    string += "!重置隊伍\n" 
    string += "!隊伍列表 直接複製整個列表輸入即可\n"  
    string += "!暫停報名\n"  
    string += "!恢復報名\n```"  
    return string

# leave_dict = {}

# def leave_cmd_list():
#     string = "```!列表\n"
#     string += "!請假 日期(YYYYmmdd) 時間 事由)\n"
#     string += "!代請 人員 日期(YYYYmmdd) 時間 事由)\n"
#     string += "```"
#     return string

# def leave_list():
#     global leave_dict
#     result = ''
#     week_day_list = {
#         0 : '一',
#         1 : '二',      
#         2 : '三',
#         3 : '四',
#         5 : '五',      
#         6 : '六',
#         7 : '日',     
#     }
#     for date in leave_dict.keys():
#         if len(leave_dict[date]) == 0:
#             continue
#         if date + timedelta(days=7) < dt.now():
#             continue
#         result += '%s(%s) : \n' % (dt.strftime(date, "%m月%d日"), week_day_list[date.weekday()])
#         count=0
#         result += '```'
#         for leave_data in leave_dict[date]:
#             result += '  %5s %10s %10s \n' % (leave_data)
#             count += 1
#         result += '共%s人' % count
#         result += '```'
#     if result == '':
#         result = "目前無人請假"
#     return result

# def help_apply_leave(user, row):
#     global leave_dict
#     data = split_by_space(row)
#     if len(data) < 5:
#         return user.mention + '正確格式為\n```!代請 人員 日期(YYYYmmdd) 時間 事由)```'
#     try:
#         date = dt.strptime(data[2], "%Y%m%d")
#     except:
#         return user.mention + '日期格式為\n```YYYYmmdd (ex:20191203)```'
#     if date not in leave_dict:
#         leave_dict[date] = []
#     leave_dict[date].append((data[1], data[3], data[4]))    
#     return user.mention + '%s 請假已登記' % date[1]

# def apply_leave(user, row):
#     global leave_dict
#     data = split_by_space(row)
#     if len(data) < 5:
#         return user.mention + '正確格式為\n```!請假 人員 日期(YYYYmmdd) 時間 事由)```'
#     try:
#         date = dt.strptime(data[2], "%Y%m%d")
#     except:
#         return user.mention + '日期格式為\n```YYYYmmdd (ex:20191203)```'
#     if date not in leave_dict:
#         leave_dict[date] = []
#     leave_dict[date].append((data[1], data[3], data[4]))
#     return user.mention + '請假已登記'



@client.event
async def on_message(message):
    global admin_role
    global quing
    global land_quing
    global guild_member_map
    global queue_channel
    global stop_quing
    if message.author == client.user:
        return
    if message.guild.id not in [QUEUE_GUILD]:
        return
    if message.channel.id in [queue_channel]:
        if message.author.display_name not in guild_member_map:
            guild_member_map[message.author.display_name] = message.author
        if message.channel.id == queue_channel:
            q = quing
    
        if message.content.startswith('!列表') or message.content.startswith('！列表'):
            await message.channel.send(respon_q_list(q))   
        elif message.content.startswith('!報名') or message.content.startswith('！報名'):
            if stop_quing == True:
                await message.channel.send('報名功能未開放')
            else:
                respon = check_queue(message.author, message.content, q)
                await message.channel.send(respon) 
        elif message.content.startswith('!代報名') or message.content.startswith('！代報名'):
            if stop_quing == True:
                await message.channel.send('報名功能未開放')
            else:
                respon = Agent_check_queue(message.author, message.mentions[0], message.content, q)
                await message.channel.send(respon)                
        elif message.content.startswith('!取消報名') or message.content.startswith('！取消報名'):
            respon = cancel_queue(message.author, message.content, q)
            await message.channel.send(respon)
        # elif message.content.startswith('!進組') or message.content.startswith('！進組'):
        #     respon = quit_queue(message.author, message.content)
        #     await message.channel.send(respon)    
        elif message.content.startswith('!移除列隊') or message.content.startswith('！移除列隊'):
            flag = True
            for role in message.author.roles:
                if role >= admin_role:
                    respon = admin_cancel_queue(message.content, q)
                    await message.channel.send(respon)    
                    flag = False
                    break
            if flag:
                await message.channel.send('抱歉，你沒權限執行 !移除列隊')
        elif message.content.startswith('!移除編號') or message.content.startswith('！移除編號'):
            flag = True
            for role in message.author.roles:
                if role >= admin_role:
                    respon = admin_cancel_queue_number(message.content, q)
                    await message.channel.send(respon)    
                    flag = False
                    break
            if flag:
                await message.channel.send('抱歉，你沒權限執行 !移除列隊')
        elif message.content.startswith('!清除隊伍') or message.content.startswith('！清除隊伍'):
            flag = True
            for role in message.author.roles:
                if role >= admin_role:
                    respon = requeue(message.author, message.content, q)
                    await message.channel.send(respon)
                    flag = False
                    break
            if flag:
                await message.channel.send('抱歉，你沒權限執行 !清除隊伍')
        elif message.content.startswith('!重置隊伍') or message.content.startswith('！重置隊伍'):
            flag = True
            for role in message.author.roles:
                if role >= admin_role:
                    respon = rmqueue(message.author, q)
                    await message.channel.send(respon)
                    flag = False
                    break
            if flag:
                await message.channel.send('抱歉，你沒權限執行 !重置隊伍')    
        elif message.content.startswith('!隊伍列表'):
            flag = True
            for role in message.author.roles:
                if role >= admin_role:
                    respon = set_queue(message.author, message.content, q)
                    await message.channel.send(respon)
                    flag = False
                    break
            if flag:
                await message.channel.send('抱歉，你沒權限執行 !隊伍列表')  
        elif message.content.startswith('!暫停報名') or message.content.startswith('！暫停報名'):
            flag = True
            for role in message.author.roles:
                if role >= admin_role:
                    stop_quing = True
                    await message.channel.send('報名功能已關閉')
                    flag = False
                    break
            if flag:
                await message.channel.send('抱歉，你沒權限執行 !暫停報名')  
        elif message.content.startswith('!恢復報名') or message.content.startswith('！恢復報名'):
            flag = True
            for role in message.author.roles:
                if role >= admin_role:
                    stop_quing = False
                    await message.channel.send('報名功能已啟動')
                    flag = False
                    break
            if flag:
                await message.channel.send('抱歉，你沒權限執行 !恢復報名')
        elif message.content == '!指令' or message.content == '！指令':
            await message.channel.send(cmd_list())
        elif message.content == 'raise-exception':
            raise discord.DiscordException
        else:
            return 

client.run(DISCORD_TOKEN)