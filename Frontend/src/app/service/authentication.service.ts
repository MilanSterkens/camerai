import {Injectable, NgZone} from '@angular/core';
import {User} from '../models/user';
import {AngularFireAuth} from '@angular/fire/compat/auth';
import {
  AngularFirestore,
  AngularFirestoreDocument,
} from '@angular/fire/compat/firestore';
import {Router} from '@angular/router';
import {CameraiService} from "./camerai.service";

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
  userData: any; // Save logged in user data
  activatedUsers: any = [];

  constructor(
    public afs: AngularFirestore, // Inject Firestore service
    public afAuth: AngularFireAuth, // Inject Firebase auth service
    public router: Router,
    public ngZone: NgZone, // NgZone service to remove outside scope warning
    public cameraiService: CameraiService
  ) {
    /* Saving user data in localstorage when
    logged in and setting up null when logged out */
    this.cameraiService.getUsers().subscribe((users) => {
      this.activatedUsers = users;
    });
    this.afAuth.authState.subscribe((user) => {
      if (user) {
        this.userData = user;
        localStorage.setItem('user', JSON.stringify(this.userData));
        JSON.parse(localStorage.getItem('user')!);
      } else {
        localStorage.setItem('user', 'null');
        JSON.parse(localStorage.getItem('user')!);
      }
    });
  }

  // Sign in with email/password
  async Login(email: string, password: string) {
    try {
      this.cameraiService.getUsers().subscribe((users) => {
        this.activatedUsers = users;
        const targetUser = this.activatedUsers.find((user: { email: string }) => user.email === email);
        if (targetUser == undefined) {
          window.alert("There is no account activated with this email address");
          return;
        }});
      const result = await this.afAuth.signInWithEmailAndPassword(email, password);
      this.afAuth.user.subscribe(async (user) => {
        if (user) {
          this.SetUserData(result.user);
          if (this.userData.emailVerified) {
            this.ngZone.run(() => {
              this.router.navigate(['home']);
            });
          }
        } else {
          localStorage.setItem('user', 'null');
        }
      });
    } catch (error) {
      window.alert(error);
    }
  }

  // Sign up with email/password
  Register(email: string, password: string) {
    this.cameraiService.getUsers().subscribe((users) => {
      this.activatedUsers = users;
      const targetUser = this.activatedUsers.find((user: { email: string }) => user.email === email);
      if (targetUser == undefined) {
        window.alert("There is no account activated with this email address");
        return;
      }
      this.afAuth
        .createUserWithEmailAndPassword(email, password)
        .then((result) => {
          this.SendVerificationMail();
          this.SetUserData(result.user);
        })
        .catch((error) => {
          window.alert(error.message);
        });
    });
  }

  // Send email verfificaiton when new user sign up
  SendVerificationMail() {
    return this.afAuth.currentUser
      .then((u: any) => u.sendEmailVerification())
      .then(() => {
        this.router.navigate(['verify-email-address']);
      });
  }

  // Reset Forggot password
  ForgotPassword(passwordResetEmail: string) {
    return this.afAuth
      .sendPasswordResetEmail(passwordResetEmail)
      .then(() => {
        window.alert('Password reset email sent, check your inbox.');
      })
      .catch((error) => {
        window.alert(error);
      });
  }

  // Returns true when user is logged in and email is verified
  get isLoggedIn(): boolean {
    const user = JSON.parse(localStorage.getItem('user')!);
    return user !== null && user.emailVerified !== false;
  }

  /* Setting up user data when sign in with username/password,
  sign up with username/password and sign in with social auth
  provider in Firestore database using AngularFirestore + AngularFirestoreDocument service */
  SetUserData(user: any) {
    const userRef: AngularFirestoreDocument<any> = this.afs.doc(
      `users/${user.uid}`
    );
    const userData: User = {
      uid: user.uid,
      email: user.email,
      emailVerified: user.emailVerified,
      displayName: user.displayName,
      photoURL: user.photoURL
    };
    return userRef.set(userData, {
      merge: true,
    });
  }

  // Sign out
  SignOut() {
    return this.afAuth.signOut().then(() => {
      localStorage.removeItem('user');
      this.router.navigate(['login']);
    });
  }
}
