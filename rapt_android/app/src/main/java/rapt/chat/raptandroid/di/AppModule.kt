package rapt.chat.raptandroid.di

import android.content.Context
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import rapt.chat.raptandroid.common.Constants
import rapt.chat.raptandroid.data.repository.AuthRepository
import rapt.chat.raptandroid.data.repository.AuthRepositoryImpl
import rapt.chat.raptandroid.data.repository.ChatRepository
import rapt.chat.raptandroid.data.repository.ChatRepositoryImpl
import rapt.chat.raptandroid.data.repository.ChatsRepository
import rapt.chat.raptandroid.data.repository.ChatsRepositoryImpl
import rapt.chat.raptandroid.data.repository.ProfileRepository
import rapt.chat.raptandroid.data.repository.ProfileRepositoryImpl
import rapt.chat.raptandroid.data.source.RaptApi
import rapt.chat.raptandroid.data.source.RaptDataStore
import rapt.chat.raptandroid.data.source.RaptDataStoreImpl
import rapt.chat.raptandroid.data.source.RaptSocketClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideRaptApi(): RaptApi {
        return Retrofit.Builder()
            .baseUrl(Constants.BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(RaptApi::class.java)
    }

    @Provides
    @Singleton
    fun provideRaptDataStore(@ApplicationContext context: Context): RaptDataStore {
        return RaptDataStoreImpl(context)
    }

    @Provides
    @Singleton
    fun provideAuthRepository(api: RaptApi, ds: RaptDataStore): AuthRepository {
        return AuthRepositoryImpl(api,ds)
    }

    @Provides
    @Singleton
    fun provideProfileRepository(api: RaptApi, authRepository: AuthRepository): ProfileRepository {
        return ProfileRepositoryImpl(api, authRepository)
    }

    @Provides
    @Singleton
    fun provideChatRoomsRepository(
        api: RaptApi,
        authRepository: AuthRepository,
        socketClient: RaptSocketClient): ChatsRepository {
        return ChatsRepositoryImpl(api, authRepository, socketClient)
    }

    @Provides
    @Singleton
    fun provideChatRepository(api: RaptApi, authRepository: AuthRepository, socketClient: RaptSocketClient, profileRepository: ProfileRepository): ChatRepository {
        return ChatRepositoryImpl(api, authRepository, socketClient, profileRepository)
    }

    @Provides
    @Singleton
    fun provideChatSocketClient(authRepository: AuthRepository): RaptSocketClient {
        return RaptSocketClient(authRepository)
    }

}