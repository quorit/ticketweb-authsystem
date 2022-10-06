

class NetworkError extends Error {
   constructor(message) {
      super(message);
      this.name="AuthSystemNetworkError"
   }
}

class HTTPResponseError extends NetworkError {
   //this error is for any http response error that is not failed session authentication
   constructor(status_code,message){
      super(message);
      this.status_code = status_code;
      this.name="AuthSystemHTTPResponseError"
   }
}


class SessionAuthenticationError extends HTTPResponseError {
   //we throw this on a 401 for session operations
   constructor(message){
      super(401,message);
      this.name="SessionAuthenticationError"
   }
}




class ConnectionError extends NetworkError {
   //this is for when a fetch fails and we don't even get a response
   constructor(message){
      super(message);
      this.name="AuthSystemConnectionError"
   }
}





function test_ok(response) {
    return new Promise ((resolve,reject) => {
       if (response.ok){
          resolve (response);
       }else{
         console.log("bye son");
         console.log(response);
         console.log(response.status);
         var str = "Server returned " + response.status + " : " + response.statusText;
         if (response.status){
               if (response.status==401){
                  //401 is HTTPUnauthorized but that really means not authenticated
                  //403 HTTPForbidden, is what really means unauthorized
                  reject(new SessionAuthenticationError(str));
               }else{
                  reject(new HTTPResponseError(response.status,str));
                  
               }
         }else{
            reject(new ConnectionError("No response status. Probably no connection to auth system"));
         }
       }
    });
}


function extended_fetch(opts,authsystem_path,app_name){
   const url = window.location.origin + authsystem_path + "session/" + app_name;

   return fetch(url,opts).then(response => response,err=> new AuthSystemConnectionError(err.message));
}



function get_app_token(authsystem_path,app_name){
   return extended_fetch(
         // should send cookie
         {   
            method: "GET",
            mode: "cors"
         },
         authsystem_path,
         app_name)
         .then(response => test_ok(response,true))
         .then(response => response.text());
         //response is just an application jwt token and we should have a renewed cookie
}

function login_session(user_id, password,authsystem_path,app_name){
   const body = JSON.stringify({
      user_id: user_id,
      password: password
   })
   return extended_fetch(
      {   
         method: "POST",
         mode: "cors",
         body: body
      },
      authsystem_path,
      app_name)
      .then(response => test_ok(response))
      // eslint-disable-next-line no-unused-vars
      .then(response => true);
      //although there is no response body, we do get a cookie as part of the response
}





function delete_session(authsystem_path,app_name){
   return extended_fetch(
      {
         method: "DELETE",
         mode: "cors"
      },
      authsystem_path,
      app_name
   ).then(response =>test_ok(response))
   // eslint-disable-next-line no-unused-vars
   .then(response => true);
}



module.exports = {get_app_token, login_session, delete_session,
        SessionAuthenticationError, 
        ConnectionError,
        HTTPResponseError,
        NetworkError
      
      }
