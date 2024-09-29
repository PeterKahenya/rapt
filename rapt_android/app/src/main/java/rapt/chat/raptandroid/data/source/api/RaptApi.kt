package rapt.chat.raptandroid.data.source.api

import rapt.chat.raptandroid.data.model.LoginRequest
import rapt.chat.raptandroid.data.model.LoginResponse
import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.data.model.ProfileUpdateRequest
import rapt.chat.raptandroid.data.model.RefreshRequest
import rapt.chat.raptandroid.data.model.RefreshResponse
import rapt.chat.raptandroid.data.model.VerifyRequest
import rapt.chat.raptandroid.data.model.VerifyResponse
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.PUT

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
    suspend fun verify(verifyRequest: VerifyRequest): VerifyResponse

    @FormUrlEncoded
    @POST("/auth/refresh")
    suspend fun refresh(refreshRequest: RefreshRequest): RefreshResponse

    // get profile
    @GET("/auth/me")
    suspend fun getProfile(@Header("Authorization") accessToken: String): ProfileResponse

    //update profile
    @PUT("/auth/users/{userId}")
    suspend fun updateProfile(
        @Header("Authorization") accessToken: String,
        profileUpdateRequest: ProfileUpdateRequest
    ): ProfileResponse


}