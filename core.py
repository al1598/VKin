import datetime
import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from config import access_token, comunity_token
from db import select_profiles, insert_profiles


class VkBot:
    def __init__(self):
        self.vk_user = vk_api.VkApi(token=access_token)
        self.vk_user_got_api = self.vk_user.get_api()
        self.vk_group = vk_api.VkApi(token=comunity_token)
        self.vk_group_got_api = self.vk_group.get_api()
        self.longpoll = VkLongPoll(self.vk_group)
        self.list_offset = 0
        self.list_count = 100
        self.sex = 0
        self.age_from = 0
        self.age_to = 0
        self.city_title = 0



    def get_user_info(self, user_id):
        try:
            user_info = self.vk_user_got_api.users.get(user_ids=user_id,
                                                       fields="bdate, "
                                                              "status, "
                                                              "sex, "
                                                              "city, "
                                                              "domain, "
                                                              "home_town, "
                                                              "can_write_private_message, ")
            return user_info
        except TypeError:
            return None



    def message_send(self, user_id, message, attachments='none'):
        try:
            self.vk_group_got_api.messages.send(
                user_id=user_id,
                message=message,
                random_id=get_random_id(),
                attachment=",".join(attachments)
            )
        except TypeError:
            pass



    def get_name(self, user_id):
        try:
            name = self.user_info[0]['first_name']
            return name
        except KeyError:
            self.message_send(user_id, "Ошибка")



    def input_age(self, user_id, age):
        a = age.split("-")
        try:
            self.age_from = int(a[0])
            self.age_to = int(a[1])
            if self.age_from == self.age_to:
                self.message_send(user_id, f' Ищем возраст: {self.age_to}')
                return
            self.message_send(user_id, f' Ищем возраст в пределах от {self.age_from} и до {self.age_to}')
            return
        except IndexError:
            self.age_to = int(age)
            self.message_send(user_id, f' Ищем возраст {self.age_to}')
            return
        except NameError:
            self.message_send(user_id, f'Ошибка')
            return
        except ValueError:
            self.message_send(user_id, f'Ошибка')
            return



    def get_age_of_person(self, bdate: str) -> object:
        bdate_splited = bdate.split(".")
        month = ""
        try:
            reverse_bdate = datetime.date(int(bdate_splited[2]), int(bdate_splited[1]), int(bdate_splited[0]))
            today = datetime.date.today()
            age = (today.year - reverse_bdate.year)
            if reverse_bdate.month >= today.month and reverse_bdate.day > today.day or reverse_bdate.month > today.month:
                age -= 1
            return age
        except IndexError:
            return



    def get_age_of_user(self, user_id):
        try:
            info = self.user_info[0]['bdate']
            print(info)
            bdate_splited = info.split(".")
            reverse_bdate = datetime.date(int(bdate_splited[2]), int(bdate_splited[1]), int(bdate_splited[0]))
            today = datetime.date.today()
            age = (today.year - reverse_bdate.year)
            if reverse_bdate.month >= today.month and reverse_bdate.day > today.day or reverse_bdate.month > today.month:
                age -= 1
            self.age_from = age
            self.age_to = age
            return print(f' Ищем вашего возраста: {age}')
        except KeyError:
            print(f'Ошибка')
            self.message_send(user_id, 'Введите ваш возраст, например "20".')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return self.input_age(user_id, age)



    def get_city(self, user_id):
        self.message_send(user_id,
                          f' Введите "да"- поиск будет произведен в вашем городе.'
                          f' Или введите: поиск'
                          )
        info = self.user_info
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                if (answer == "да") and ("city" in info[0]):
                    self.city_id = info[0]['city']["id"]
                    self.city_title = info[0]['city']["title"]
                    return
                elif (answer != "да" ):
                    cities = self.vk_user_got_api.database.getCities(
                        country_id=1,
                        q=answer.capitalize(),
                        need_all=1,
                        count=1000
                    )['items']
                    if len(cities) == 0:
                        self.message_send(user_id,
                                          f'Введите название города для поиска, например: "Москва"'
                                          )
                    for i in cities:
                        if i["title"] == answer.capitalize():
                            self.city_id = i["id"]
                            self.city_title = answer.capitalize()
                            return
                else:
                    self.message_send(user_id,
                                      f'Введите название города для поиска, например: "Москва"'
                                      )



    def gender(self, user_id):
        info = self.user_info
        gender = 3 - info[0]['sex']
        if gender == 1:
            print('Ищем женщину.')
            return gender
        elif gender == 2:
            print('Ищем мужчину.')
            return gender
        else:
            gender == 0
            print('Ищем людей любого пола')
            return gender



    def vk_persons_search(self, user_id, list_offset, list_count):
        try:
            res = self.vk_user_got_api.users.search(
                sort=0,
                offset=list_offset,
                city=self.city_id,
                sex=self.gender(user_id),
                status=1,
                age_from=self.age_from,
                age_to=self.age_to,
                has_photo=1,
                count=list_count,
                fields="can_write_private_message, " 
                       "city, "
                       "domain, "
            )
            print("list_offset ", list_offset)
            return res
        except:
            return None

    def searching_for_person(self, user_id):
        global founded_persons
        founded_persons = []
        res = self.vk_persons_search(user_id, self.list_offset, self.list_count)
        number = 0
        try:
            for person in res["items"]:
                if not person["is_closed"]:
                    if "city" in person and person["city"]["id"] == self.city_id and person["city"]["title"] == self.city_title:
                        number += 1
                        id_vk = person["id"]
                        founded_persons.append(id_vk)
            print(f'Найдено {number} открытых профилей из {res["count"]}')
            print(founded_persons)
            print(len(founded_persons))
        except:
            print("Ошибка")
        return



    def get_photos(self, user_id):
        res = self.vk_user_got_api.photos.get(
            owner_id=user_id,
            album_id="profile",
            extended=1,
            count=30
        )
        dict_photos = dict()
        for i in res['items']:
            photo_id = str(i["id"])
            i_likes = i["likes"]
            if i_likes["count"]:
                likes = i_likes["count"]
                dict_photos[likes] = photo_id
        list_of_ids = sorted(dict_photos.items(), reverse=True)
        attachments = []
        photo_ids = []
        for i in list_of_ids:
            photo_ids.append(i[1])
        for i in range(len(photo_ids)):
            if i > 2:
                break
            attachments.append('photo{}_{}'.format(user_id, photo_ids[i]))
        return attachments



    def get_person_id(self, user_id):
        seen_person = []
        for i in select_profiles():
            seen_person.append(int(i[0]))
        if not seen_person:
            try:
                return founded_persons[0]
            except NameError:
                return None
        else:
            try:
                for id in founded_persons:
                    if id in seen_person:
                        pass
                    else:
                        return id
                else:
                    self.list_offset += self.list_count
                    self.searching_for_person(user_id)
                    if len(founded_persons) == 0:
                        return None
                    return self.get_person_id(user_id)
            except NameError:
                try:
                    return founded_persons[0]
                except NameError:
                    return None


    def found_person_info(self, show_person_id):
        res = self.get_user_info(user_id=show_person_id)
        first_name = res[0]["first_name"]
        last_name = res[0]["last_name"]
        age = self.get_age_of_person(res[0]["bdate"])
        vk_link = 'vk.com/' + res[0]["domain"]
        city = ''
        try:
            if res[0]["city"]["title"] is not None:
                city = f'Город {res[0]["city"]["title"]}'
            else:
                city = f'Город {res[0]["home_town"]}'
        except KeyError:
            pass
        print(f'{first_name} {last_name}, {age}, {city}. {vk_link}')
        return f'{first_name} {last_name}, {age}, {city}. {vk_link}'



    def show_person(self, user_id):
        if self.get_person_id(user_id) == None:
            self.message_send(user_id,
                              f'Вы просмотрели все доступные анкеты. Будет выполнен повторный поиск. \n'
                              f'Измените возрастной диапазон или город. \n'
                              f'Введите возрастной диапазон, например от 20 до 30 лет в формате : 20-30 (или конкретный возраст, например: 20).')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    self.list_offset = 0
                    self.input_age(user_id, age)
                    self.get_city(user_id)
                    self.searching_for_person(user_id)
                    self.show_person(user_id)
                    return
        else:
            self.message_send(user_id, self.found_person_info(self.get_person_id(user_id)),self.get_photos(self.get_person_id(user_id)))
            insert_profiles(self.get_person_id(user_id))


bot = VkBot()
