package rapt.chat.raptandroid.data.source

import rapt.chat.raptandroid.data.model.*
import retrofit2.http.*

data class APIContactUpload(
    val phone: String,
    val name: String
)

data class APIContactUpdate(
    val name: String,
    val contactId: String
)

interface RaptApi {

    @FormUrlEncoded
    @POST("auth/login")
    suspend fun login(
        @Field("phone") phone: String,
        @Field("client_id") clientId: String,
        @Field("client_secret") clientSecret: String
    ): LoginResponse

    @FormUrlEncoded
    @POST("auth/verify")
    suspend fun verify(
        @Field("phone_verification_code") phoneVerificationCode: String,
        @Field("phone") phone: String,
        @Field("client_id") clientId: String,
        @Field("client_secret") clientSecret: String
    ): VerifyResponse

    @FormUrlEncoded
    @POST("auth/refresh")
    suspend fun refresh(
        @Field("access_token")
        accessToken: String,
        @Field("client_id")
        clientId: String,
        @Field("client_secret")
        clientSecret: String
    ): RefreshResponse

    // get profile
    @GET("auth/me")
    suspend fun getProfile(
        @Header("Authorization") accessToken: String
    ): ProfileResponse

    //update profile
    @PUT("auth/users/{userId}")
    suspend fun updateProfile(
        @Path("userId") userId: String,
        @Header("Authorization") accessToken: String,
        @Body profileUpdateRequest: ProfileUpdateRequest
    ): ProfileResponse

    // get contacts
    @GET("auth/users/{userId}/contacts")
    suspend fun getContacts(
        @Header("Authorization") accessToken: String,
        @Path("userId") userId: String
    ): List<APIContact>

    // add contacts
    @POST("auth/users/{userId}/contacts")
    suspend fun addContacts(
        @Header("Authorization") accessToken: String,
        @Path("userId") userId: String,
        @Body addContactsRequest: List<APIContactUpload>
    ): List<APIContact>

    // update contact
    @PUT("auth/users/{userId}/contacts")
    suspend fun updateContact(
        @Header("Authorization") accessToken: String,
        @Path("userId") userId: String,
        @Body updateContactsRequest: List<APIContactUpdate>
    ): List<APIContact>

    // get chat rooms
    @GET("chat/rooms")
    suspend fun getChatRooms(@Header("Authorization") accessToken: String): List<APIChatRoom>

    // create chat room
    @POST("chat/rooms")
    suspend fun createChatRoom(
        @Header("Authorization") accessToken: String,
        @Body chatRoomRequest: ChatRoomCreate
    ): APIChatRoom

    // get chat room
    @GET("chat/rooms/{roomId}")
    suspend fun getChatRoom(
        @Path("roomId") roomId: String,
        @Header("Authorization") accessToken: String
    ): APIChatRoom


    // update chat room
    @PUT("chat/rooms/{roomId}")
    suspend fun updateChatRoom(
        @Path("roomId") roomId: String,
        @Header("Authorization") accessToken: String,
        @Body chatRoomRequest: ChatRoomUpdate
    ): APIChatRoom

    // delete chat room
    @DELETE("chat/rooms/{roomId}")
    suspend fun deleteChatRoom(
        @Path("roomId") roomId: String,
        @Header("Authorization") accessToken: String
    ): Nothing


}