import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  CognitoUserAttribute,
} from 'amazon-cognito-identity-js'

const poolData = {
  UserPoolId: import.meta.env.VITE_USER_POOL_ID || 'us-east-1_vubkuLAuu',
  ClientId: import.meta.env.VITE_USER_POOL_CLIENT_ID || '5une31baabnucbe0pn2glnhk24',
}

const userPool = new CognitoUserPool(poolData)

export interface SignUpParams {
  email: string
  password: string
  name: string
}

export interface SignInParams {
  email: string
  password: string
}

export const auth = {
  signUp: (params: SignUpParams): Promise<any> => {
    return new Promise((resolve, reject) => {
      const attributeList = [
        new CognitoUserAttribute({ Name: 'email', Value: params.email }),
        new CognitoUserAttribute({ Name: 'name', Value: params.name }),
      ]

      userPool.signUp(
        params.email,
        params.password,
        attributeList,
        [],
        (err, result) => {
          if (err) {
            reject(err)
            return
          }
          resolve(result)
        }
      )
    })
  },

  confirmSignUp: (email: string, code: string): Promise<any> => {
    return new Promise((resolve, reject) => {
      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool,
      })

      cognitoUser.confirmRegistration(code, true, (err, result) => {
        if (err) {
          reject(err)
          return
        }
        resolve(result)
      })
    })
  },

  signIn: (params: SignInParams): Promise<any> => {
    return new Promise((resolve, reject) => {
      const authenticationDetails = new AuthenticationDetails({
        Username: params.email,
        Password: params.password,
      })

      const cognitoUser = new CognitoUser({
        Username: params.email,
        Pool: userPool,
      })

      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: (result) => {
          resolve(result)
        },
        onFailure: (err) => {
          reject(err)
        },
      })
    })
  },

  signOut: (): void => {
    const cognitoUser = userPool.getCurrentUser()
    if (cognitoUser) {
      cognitoUser.signOut()
    }
  },

  getCurrentUser: (): CognitoUser | null => {
    return userPool.getCurrentUser()
  },

  getSession: (): Promise<any> => {
    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser()
      if (!cognitoUser) {
        reject(new Error('No user found'))
        return
      }

      cognitoUser.getSession((err: any, session: any) => {
        if (err) {
          reject(err)
          return
        }
        resolve(session)
      })
    })
  },

  getIdToken: async (): Promise<string | null> => {
    try {
      const session = await auth.getSession()
      return session.getIdToken().getJwtToken()
    } catch {
      return null
    }
  },
}
