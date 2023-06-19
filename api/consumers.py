import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import ChatMessage, Thread

User = get_user_model()

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        print("Channel Name... ", self.channel_name)

        self.trainer_id = self.scope['url_route']['kwargs']['trainer_id']
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        print("userid",self.trainer_id)
        print("thread_id",self.thread_id)
       

        chat_room = f'user_chatroom_{self.thread_id}'
        # chat_room = 'sham'
        print("chat_room",chat_room)
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        print(received_data)
        user = await database_sync_to_async(User.objects.get)(id=self.trainer_id)
        print(user)
        msg = received_data.get('message')
        sent_by_id = received_data.get('user')
        print("send chyna aal",sent_by_id)
        send_to_id = received_data.get('send_to')
        print("sending to whome",send_to_id)
        thread_id = received_data.get('thread_id')
        print(thread_id)

        if not msg:
            print('Error:: empty message')
            return False

        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id)
        if not sent_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect')
        if not thread_obj:
            print('Error:: Thread id is incorrect')

        await self.create_chat_message(thread_obj, sent_by_user, msg)
        response = {
            'message': msg,
            'sent_by': sent_by_id,
            'send_to':send_to_id,
            'thread_id': thread_id
        }
        print(response)

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'message': json.dumps(response)
            }
        )
       


    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def chat_message(self, event):
        print("thisevebt",event)
        message = event.get('message')
        print('message in chat',message)
        # send msg to group
        print("dumping",message)


        await self.send({
                'type': 'websocket.send',
                'text': message,
            })
        # await self.send(message=json.dumps({'message':message}))
    


    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj
    
    
    @database_sync_to_async
    def create_chat_message(self, thread, user, msg):
        return ChatMessage.objects.create(
            thread=thread,
            sender=user,
            message=msg
        )
    



     # await self.save_message(received_data, thread_id)

        # other_user_chat_room = f'user_chatroom_{send_to_id}'
        # self_user = self.scope['user']
        # response = {
        #     'message': msg,
        #     'sent_by': sent_by_id,
        #     'send_to':send_to_id,
        #     'thread_id': thread_id
        # }

        # await self.channel_layer.group_send(
        #     other_user_chat_room,
        #     {
        #         'type': 'chat_message',
        #         'text': json.dumps(response)
        #     }
        # )
        # await self.send({
        #     'type': 'websocket.send',
        #     'text': json.dumps(response)
        # })

# User = get_user_model()

# class ChatConsumer(AsyncConsumer):
#     async def websocket_connect(self, event):
#         print('connected', event)
#         print("Channel Name... ", self.channel_name)

#         self.trainer_id = self.scope['url_route']['kwargs']['trainer_id']
#         print("userid",self.trainer_id)
       

#         chat_room = f'user_chatroom_{self.trainer_id}'
#         print("chat_room",chat_room)
#         self.chat_room = chat_room
#         await self.channel_layer.group_add(
#             chat_room,
#             self.channel_name
#         )
#         await self.send({
#             'type': 'websocket.accept'
#         })

#     async def websocket_receive(self, event):
#         print('receive', event)
#         received_data = json.loads(event['text'])
#         print(received_data)
#         user = await database_sync_to_async(User.objects.get)(id=self.trainer_id)
#         print(user)
#         msg = received_data.get('message')
#         sent_by_id = received_data.get('user')
#         print("send chyna aal",sent_by_id)
#         send_to_id = received_data.get('send_to')
#         print("sending to whome",send_to_id)
#         thread_id = received_data.get('thread_id')
#         print(thread_id)

#         if not msg:
#             print('Error:: empty message')
#             return False

#         sent_by_user = await self.get_user_object(sent_by_id)
#         send_to_user = await self.get_user_object(send_to_id)
#         thread_obj = await self.get_thread(thread_id)
#         if not sent_by_user:
#             print('Error:: sent by user is incorrect')
#         if not send_to_user:
#             print('Error:: send to user is incorrect')
#         if not thread_obj:
#             print('Error:: Thread id is incorrect')

#         # await self.create_chat_message(thread_obj, sent_by_user, msg)
#         await self.save_message(received_data, thread_id)

#         other_user_chat_room = f'user_chatroom_{send_to_id}'
#         # self_user = self.scope['user']
#         response = {
#             'message': msg,
#             'sent_by': sent_by_id,
#             'send_to':send_to_id,
#             'thread_id': thread_id
#         }

#         await self.channel_layer.group_send(
#             other_user_chat_room,
#             {
#                 'type': 'chat_message',
#                 'text': json.dumps(response)
#             }
#         )
#         await self.send({
#             'type': 'websocket.send',
#             'text': json.dumps(response)
#         })


#         # await self.channel_layer.group_send(
#         #     self.chat_room,
#         #     {
#         #         'type': 'chat_message',
#         #         'text': json.dumps(response)
#         #     }
#         # )
        

#     async def websocket_disconnect(self, event):
#         print('disconnect', event)

#     async def chat_message(self, event):
#         print('chat_message', event)
#         message = event.get('message')
#         print("nn",message)
#         if message:
#             await self.send({
#                 'type': 'websocket.send',
#                 'text': json.dumps(message)
#             })

#     # async def chat_message(self, event):
#     #     print('chat_message', event)
#     #     await self.send({
#     #         'type': 'websocket.send',
#     #         'text': event['text']
#     #     })
#     async def save_message(self, message, thread_id):
#         thread = await self.get_thread(thread_id)
#         if thread is None:
#             return

#         sender = message.get('sent_by')
#         message_text = message.get('message')

#         user = await self.get_user_object(sender)
#         if user is None:
#             return

#         chat_message = await self.create_chat_message(thread, user, message_text)

#         await self.channel_layer.group_send(
#             self.chat_room,
#             {
#                 'type': 'chat_message',
#                 'message': self.serialize_message(chat_message),
#             }
#         )
#     def serialize_message(self, message):
#         return {
#             'id': message.id,
#             'thread': message.thread.id,
#             'sender': message.sender.id,
#             'message': message.message,
#             'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
#         }
#     @database_sync_to_async
#     def get_user_object(self, user_id):
#         qs = User.objects.filter(id=user_id)
#         if qs.exists():
#             obj = qs.first()
#         else:
#             obj = None
#         return obj

#     @database_sync_to_async
#     def get_thread(self, thread_id):
#         qs = Thread.objects.filter(id=thread_id)
#         if qs.exists():
#             obj = qs.first()
#         else:
#             obj = None
#         return obj
    
    
#     @database_sync_to_async
#     def create_chat_message(self, thread, user, msg):
#         return ChatMessage.objects.create(
#             thread=thread,
#             sender=user,
#             message=msg
#         )

# import json
# from channels.consumer import AsyncConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth import get_user_model

# from .models import ChatMessage, Thread

# User = get_user_model()

# class ChatConsumer(AsyncConsumer):
#     async def websocket_connect(self, event):
#         print('connected', event)
#         print("Channel Name... ", self.channel_name)

#         self.trainer_id = self.scope['url_route']['kwargs']['trainer_id']
#         print("userid",self.trainer_id)
       

#         chat_room = f'user_chatroom_{self.trainer_id}'
#         print("chat_room",chat_room)
#         self.chat_room = chat_room
#         await self.channel_layer.group_add(
#             chat_room,
#             self.channel_name
#         )
#         await self.send({
#             'type': 'websocket.accept'
#         })

#     async def websocket_receive(self, event):
#         print('receive', event)
#         received_data = json.loads(event['text'])
#         print(received_data)
#         user = await database_sync_to_async(User.objects.get)(id=self.trainer_id)
#         print(user)
#         msg = received_data.get('message')
#         sent_by_id = received_data.get('send_by')
#         print("send chyna aal",sent_by_id)
#         send_to_id = received_data.get('send_to')
#         print("sending to whome",send_to_id)
#         # thread_id = received_data.get('thread_id')

#         if not msg:
#             print('Error:: empty message')
#             return False

#         sent_by_user = await self.get_user_object(sent_by_id)
#         send_to_user = await self.get_user_object(send_to_id)
#         # thread_obj = await self.get_thread(thread_id)
#         if not sent_by_user:
#             print('Error:: sent by user is incorrect')
#         if not send_to_user:
#             print('Error:: send to user is incorrect')
#         # if not thread_obj:
#         #     print('Error:: Thread id is incorrect')

#         # await self.create_chat_message(thread_obj, sent_by_user, msg)

#         other_user_chat_room = f'user_chatroom_{send_to_id}'
#         # self_user = self.scope['user']
#         response = {
#             'message': msg,
#             'sent_by': sent_by_id,
#             'send_to':send_to_id
#             # 'thread_id': thread_id
#         }

#         await self.channel_layer.group_send(
#             other_user_chat_room,
#             {
#                 'type': 'chat_message',
#                 'text': json.dumps(response)
#             }
#         )
#         await self.send({
#             'type': 'websocket.send',
#             'text': json.dumps(response)
#         })

        
#         # await self.channel_layer.group_send(
#         #     self.chat_room,
#         #     {
#         #         'type': 'chat_message',
#         #         'text': json.dumps(response)
#         #     }
#         # )

#     async def websocket_disconnect(self, event):
#         print('disconnect', event)

#     async def chat_message(self, event):
#         print('chat_message', event)
#         await self.send({
#             'type': 'websocket.send',
#             'text': event['text']
#         })

#     @database_sync_to_async
#     def get_user_object(self, user_id):
#         qs = User.objects.filter(id=user_id)
#         if qs.exists():
#             obj = qs.first()
#         else:
#             obj = None
#         return obj

#     @database_sync_to_async
#     def get_thread(self, thread_id):
#         qs = Thread.objects.filter(id=thread_id)
#         if qs.exists():
#             obj = qs.first()
#         else:
#             obj = None
#         return obj

#     @database_sync_to_async
#     def create_chat_message(self, thread, user, msg):
#         ChatMessage.objects.create(thread=thread, user=user, message=msg)

    # async def chat_message(self, event):
    #     print('chat_message', event)
    #     message = event.get('message')
    #     print("ehhht",message)

    #     if message:
    #         print("herechta",message)
            
    #         await self.send({
    #             'type': 'websocket.send',
    #             'message': json.dumps(message)
    #         })

    # async def chat_message(self, event):
    #     print('chat_message', event)
    #     await self.send({
    #         'type': 'websocket.send',
    #         'text': event['text']
    #     })
    # async def save_message(self, message, thread_id):
    #     thread = await self.get_thread(thread_id)
    #     if thread is None:
    #         return

    #     sender_id = message.get('sent_by')
    #     message_text = message.get('message')

    #     user = await self.get_user_object(sender_id)
    #     if user is None:
    #         return

    #     chat_message = await self.create_chat_message(thread, user, message_text)

    #     await self.channel_layer.group_send(
    #         self.chat_room,
    #         {
    #             'type': 'chat_message',
    #             'message': self.serialize_message(chat_message),
    #         }
    #     )
    # def serialize_message(self, message):
    #     return {
    #         'id': message.id,
    #         'thread_id': message.thread.id,
    #         'sender': message.sender.id,
    #         'message': message.message,
    #         'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
    #     }