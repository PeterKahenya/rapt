package rapt.chat.raptandroid.di

import android.content.Context
import android.os.Build
import android.util.Log
import androidx.annotation.RequiresApi
import androidx.room.Room
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.websocket.WebSockets
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response
import rapt.chat.raptandroid.common.Constants
import rapt.chat.raptandroid.data.repository.AuthRepository
import rapt.chat.raptandroid.data.repository.AuthRepositoryImpl
import rapt.chat.raptandroid.data.repository.ChatRepository
import rapt.chat.raptandroid.data.repository.ChatRepositoryImpl
import rapt.chat.raptandroid.data.repository.ChatRoomsRepository
import rapt.chat.raptandroid.data.repository.ChatRoomsRepositoryImpl
import rapt.chat.raptandroid.data.repository.ContactsRepository
import rapt.chat.raptandroid.data.repository.ContactsRepositoryImpl
import rapt.chat.raptandroid.data.repository.ProfileRepository
import rapt.chat.raptandroid.data.repository.ProfileRepositoryImpl
import rapt.chat.raptandroid.data.source.ChatRoomDao
import rapt.chat.raptandroid.data.source.ContactDao
import rapt.chat.raptandroid.data.source.RaptApi
import rapt.chat.raptandroid.data.source.RaptContentProvider
import rapt.chat.raptandroid.data.source.RaptDataStore
import rapt.chat.raptandroid.data.source.RaptDataStoreImpl
import rapt.chat.raptandroid.data.source.RaptDatabase
import rapt.chat.raptandroid.data.source.RaptSocketClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.time.Duration
import javax.inject.Singleton

class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        Log.d("RaptNetworkCall:", "Request: ${request.method()} ${request.url()} ${request.headers()} ${request.body()}")
        val response = chain.proceed(request)
        Log.d("RaptNetworkCall:", "Response: ${response.code()} ${response.message()} ${response.headers()} ${response.body().toString()}")
        return response
    }
}

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @RequiresApi(Build.VERSION_CODES.O)
    @Provides
    @Singleton
    fun provideRaptApi(): RaptApi {
        val loggingInterceptor = LoggingInterceptor()
        val okHttpClient: OkHttpClient = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(Duration.ofSeconds(30))
            .writeTimeout(Duration.ofSeconds(30))
            .readTimeout(Duration.ofSeconds(30))
            .build()
        return Retrofit.Builder()
            .baseUrl(Constants.BASE_URL)
            .client(okHttpClient)
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
    fun providesRaptDataBase(@ApplicationContext context: Context): RaptDatabase {
        return Room.databaseBuilder(context, RaptDatabase::class.java, "rapt_db")
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    @Singleton
    fun provideContactDao(db: RaptDatabase): ContactDao = db.contactDao()

    @Provides
    @Singleton
    fun provideChatRoomDao(db: RaptDatabase): ChatRoomDao = db.chatRoomDao()

    @Provides
    @Singleton
    fun provideAuthRepository(api: RaptApi, ds: RaptDataStore): AuthRepository {
        return AuthRepositoryImpl(api,ds)
    }

    @Provides
    @Singleton
    fun provideContentProvider(@ApplicationContext context: Context): RaptContentProvider {
        return RaptContentProvider(context)
    }

    @Provides
    @Singleton
    fun provideContactsRepository(
        api: RaptApi,
        contactDao: ContactDao,
        contentProvider: RaptContentProvider,
        authRepository: AuthRepository
        ): ContactsRepository {
        return ContactsRepositoryImpl(api,contactDao,contentProvider,authRepository)
    }

    @Provides
    @Singleton
    fun provideProfileRepository(
        api: RaptApi,
        authRepository: AuthRepository
    ): ProfileRepository {
        return ProfileRepositoryImpl(api, authRepository)
    }

    @Provides
    @Singleton
    fun provideChatRoomsRepository(
        api: RaptApi,
        chatRoomDao: ChatRoomDao,
        contactDao: ContactDao,
        authRepository: AuthRepository,
        socketClient: RaptSocketClient
    ): ChatRoomsRepository {
        return ChatRoomsRepositoryImpl(
            api,chatRoomDao,contactDao, authRepository, socketClient)
    }

    @Provides
    @Singleton
    fun provideChatRepository(
        api: RaptApi,
        chatRoomDao: ChatRoomDao,
        contactDao: ContactDao,
        authRepository: AuthRepository,
        socketClient: RaptSocketClient,
        profileRepository: ProfileRepository
    ): ChatRepository {
        return ChatRepositoryImpl(
            api, chatRoomDao, contactDao, authRepository, socketClient, profileRepository)
    }

    @Provides
    @Singleton
    fun provideChatSocketClient(authRepository: AuthRepository): RaptSocketClient {
        val client = HttpClient(CIO) {
            install(WebSockets){
//                pingInterval = 60000
                maxFrameSize = Long.MAX_VALUE
            }
        }
        return RaptSocketClient(authRepository,client)
    }

}