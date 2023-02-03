import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {catchError, Observable, retry, throwError} from "rxjs";
import {Device} from "../models/device";

@Injectable({
  providedIn: 'root'
})
export class CameraiService {
  constructor(private httpClient: HttpClient) {}
  getDevices(): Observable<Device[]> {
    return this.httpClient
      .get<Device[]>(`https://camerai-api.azurewebsites.net/device`)
      .pipe(
        retry(1),
        catchError(this.handleError)
      );
  }
  getDevice(deviceUniqueId: string): Observable<any[]> {
    return this.httpClient
      .get<any[]>(`https://camerai-api.azurewebsites.net/device/${deviceUniqueId}`)
      .pipe(
        retry(1),
        catchError(this.handleError)
      );
  }

  getMaxSpeed(deviceUniqueId: string, longitude: number, latitude: number): Observable<Array<{ type: number, maxSpeed: number }>> {
    return this.httpClient
      .get<[]>(`https://camerai-api.azurewebsites.net/device/getmaxspeedbydevice?uniqueId=${deviceUniqueId}&longitude=${longitude}&latitude=${latitude}`)
      .pipe(
        retry(1),
        catchError(this.handleError)
      );
  }

  postMaxSpeed(vehicleType: number, maxSpeed: number, deviceUniqueId: string, longitude: number, latitude: number): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.httpClient.post<any>(`https://camerai-api.azurewebsites.net/Device/setmaxspeed?vehicleType=${vehicleType}&maxSpeed=${maxSpeed}&deviceUniqueId=${deviceUniqueId}&longitude=${longitude}&latitude=${latitude}`, httpOptions);
  }

  getUsers(): Observable<any[]> {
    return this.httpClient
      .get<[]>(`https://camerai-api.azurewebsites.net/user`)
      .pipe(
        retry(1),
        catchError(this.handleError)
      );
  }

  getUser(id: number): Observable<any> {
    return this.httpClient
      .get<any>(`https://camerai-api.azurewebsites.net/user/${id}`)
      .pipe(
        retry(1),
        catchError(this.handleError)
      );
  }

  postUser(user: any): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.httpClient.post<any>(`https://camerai-api.azurewebsites.net/user`, user, httpOptions);
  }

  putUser(user: any, id: number): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.httpClient.post<any>(`https://camerai-api.azurewebsites.net/user/${id}`, user, httpOptions);
  }

  deleteUser(id: number): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.httpClient.delete<any>(`https://camerai-api.azurewebsites.net/user/${id}`, httpOptions);
  }

  handleError(error: any) {
    let errorMessage = '';
    if (error.error instanceof ErrorEvent) {
      // Get client-side error
      errorMessage = error.error.message;
    } else {
      // Get server-side error
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    console.log(errorMessage);
    return throwError(errorMessage);
  }
}
