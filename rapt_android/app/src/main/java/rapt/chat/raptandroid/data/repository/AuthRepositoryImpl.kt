package rapt.chat.raptandroid.data.repository

import rapt.chat.raptandroid.data.model.LoginRequest
import rapt.chat.raptandroid.data.model.LoginResponse
import rapt.chat.raptandroid.data.model.RefreshRequest
import rapt.chat.raptandroid.data.model.RefreshResponse
import rapt.chat.raptandroid.data.model.VerifyRequest
import rapt.chat.raptandroid.data.model.VerifyResponse
import rapt.chat.raptandroid.data.source.api.RaptApi
import rapt.chat.raptandroid.domain.repository.AuthRepository
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val api: RaptApi
): AuthRepository {
    override suspend fun login(loginRequest: LoginRequest): LoginResponse {
        return api.login(loginRequest.phone, loginRequest.clientId, loginRequest.clientSecret)
    }

    override suspend fun verify(verifyRequest: VerifyRequest): VerifyResponse {
        return api.verify(verifyRequest)
    }

    override suspend fun refresh(refreshRequest: RefreshRequest): RefreshResponse {
        return api.refresh(refreshRequest)
    }
}