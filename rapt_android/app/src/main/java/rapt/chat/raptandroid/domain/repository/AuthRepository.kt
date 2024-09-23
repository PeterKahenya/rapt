package rapt.chat.raptandroid.domain.repository

import rapt.chat.raptandroid.data.model.LoginRequest
import rapt.chat.raptandroid.data.model.LoginResponse
import rapt.chat.raptandroid.data.model.RefreshRequest
import rapt.chat.raptandroid.data.model.RefreshResponse
import rapt.chat.raptandroid.data.model.VerifyRequest
import rapt.chat.raptandroid.data.model.VerifyResponse

interface AuthRepository {
    suspend fun login(loginRequest: LoginRequest): LoginResponse
    suspend fun verify(verifyRequest: VerifyRequest): VerifyResponse
    suspend fun refresh(refreshRequest: RefreshRequest): RefreshResponse
}