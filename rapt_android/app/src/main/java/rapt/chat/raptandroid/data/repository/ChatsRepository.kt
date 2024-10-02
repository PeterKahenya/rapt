package rapt.chat.raptandroid.data.repository

import io.ktor.websocket.WebSocketSession
import rapt.chat.raptandroid.data.model.ChatRoom
import rapt.chat.raptandroid.data.source.RaptApi
import rapt.chat.raptandroid.data.source.RaptSocketClient
import javax.inject.Inject

data class ChatRoomSocket(
    val room: ChatRoom,
    val socket: WebSocketSession
)

interface ChatsRepository {
    suspend fun getChatRooms(): List<ChatRoom>
    suspend fun connectToChatRooms(chatRooms: List<ChatRoom>): List<ChatRoomSocket>
}

class ChatsRepositoryImpl @Inject constructor(
    private val api: RaptApi,
    private val authRepository: AuthRepository,
    private val socketClient: RaptSocketClient
): ChatsRepository {

    override suspend fun getChatRooms(): List<ChatRoom> {
        println("Getting chat rooms")
        val auth = authRepository.auth()
        println("Auth: $auth")
        return api.getChatRooms(
            accessToken = "Bearer ${auth?.accessToken}"
        )
    }

    override suspend fun connectToChatRooms(chatRooms: List<ChatRoom>): List<ChatRoomSocket> {
        val auth = authRepository.auth()
        val chatRoomsSockets = mutableListOf<ChatRoomSocket>()
        for (room in chatRooms) {
            val socket = socketClient.connect("ws://rapt.chat/api/chatsocket/${room.id}")
//            socketClient.startListening()
            chatRoomsSockets.add(ChatRoomSocket(room, socket))
        }
        return chatRoomsSockets
    }
}