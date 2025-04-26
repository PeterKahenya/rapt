package android.rapt.chat.di

import android.content.Context
import android.os.Build
import android.rapt.chat.common.RaptConstants
import android.rapt.chat.repositories.AuthRepository
import android.rapt.chat.repositories.AuthRepositoryImpl
import android.rapt.chat.repositories.ContactsRepository
import android.rapt.chat.repositories.ContactsRepositoryImpl
import android.rapt.chat.repositories.ProfileRepository
import android.rapt.chat.repositories.ProfileRepositoryImpl
import android.rapt.chat.sources.ContactDao
import android.rapt.chat.sources.RaptAPI
import android.rapt.chat.sources.RaptContentProvider
import android.rapt.chat.sources.RaptDataStoreImpl
import android.rapt.chat.sources.RaptDatabase
import android.rapt.chat.sources.RaptDatastore
import androidx.annotation.RequiresApi
import androidx.room.Room
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.time.Duration
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @RequiresApi(Build.VERSION_CODES.O)
    @Provides
    @Singleton
    fun provideRaptApi(): RaptAPI {
        val okHttpClient: OkHttpClient = OkHttpClient.Builder()
            .connectTimeout(Duration.ofSeconds(30))
            .writeTimeout(Duration.ofSeconds(30))
            .readTimeout(Duration.ofSeconds(30))
            .build()
        return Retrofit.Builder()
            .baseUrl(RaptConstants.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(RaptAPI::class.java)
    }

    @Provides
    @Singleton
    fun provideRaptDataStore(@ApplicationContext context: Context): RaptDatastore {
        return RaptDataStoreImpl(context)
    }

    @Provides
    @Singleton
    fun providesRaptDataBase(@ApplicationContext context: Context): RaptDatabase {
        return Room.databaseBuilder(context, RaptDatabase::class.java, "rapt_db").build()
    }

    @Provides
    @Singleton
    fun provideContactDao(db: RaptDatabase): ContactDao = db.contactDao()

    @Provides
    @Singleton
    fun provideAuthRepository(api: RaptAPI, ds: RaptDatastore): AuthRepository {
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
        api: RaptAPI,
        contactDao: ContactDao,
        contentProvider: RaptContentProvider,
        authRepository: AuthRepository
    ): ContactsRepository {
        return ContactsRepositoryImpl(api,contactDao,contentProvider,authRepository)
    }

    @Provides
    @Singleton
    fun provideProfileRepository(
        api: RaptAPI,
        authRepository: AuthRepository
    ): ProfileRepository {
        return ProfileRepositoryImpl(api, authRepository)
    }
}