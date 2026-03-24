const devel_mode = process.env.NODE_ENV === 'development';
// devel_mode = false; //only because I am testing the queen's web portal.

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
         console.log("About to resolve response");
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
   console.log ("sorry natalie 2");
   console.log(url);
   const result = fetch(url,opts).then(response => response,err=> new ConnectionError(err.message));
   console.log ("sorry natalie 3");
   console.log(url);
   console.log(opts);
   console.log (result);
   return result;
}



function get_app_token(authsystem_path,app_name,auth_token=null){

   //The auth token is a jwt token, either from our own devel portal, or from the ms portal
   //It's used to set up a session, if we don't already have one.
   var opts = {   
      method: "GET",
      mode: "cors"
   }

   if(auth_token){
      opts.headers = new Headers({
         "Authorization": "Bearer " + auth_token
       });
   }
   return extended_fetch(
         // should send cookie
         opts,
         authsystem_path,
         app_name)
         .then(response => test_ok(response,true))
         .then(response => response.json());
         //response has form
         // { 
         //   "jwt_token": <token>,
         //   "user_data": {
         //       "net_id": <blah>,
         //       "real_name": <blah>
         //       "email": <blah>
         //    }      
         //   
         // }
}



async function getIdToken_ms (code,  redirect_uri,client_id, tenant_id,verifier) {
  // 1. Retrieve the verifier

  // 2. Prepare the parameters for the POST body
  // Note: These must be URL-encoded, not JSON


  const params = new URLSearchParams();
  params.append('client_id', client_id);
  params.append('grant_type', 'authorization_code');
  params.append('code', code);
  params.append('redirect_uri', redirect_uri);
  params.append('code_verifier', verifier);

  try {
    const fetch_url = `https://login.microsoftonline.com/${tenant_id}/oauth2/v2.0/token`
    const response = await fetch(fetch_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params
    });

    const data = await response.json();

    if (data.id_token) {
      // SUCCESS!
      console.log("Tokens received:", data);
      
      
      return data.id_token;
    } else {
      console.error("Token error:", data.error_description);
    }
  } catch (error) {
    console.error("Network error during token exchange:", error);
  }
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





module.exports = {get_app_token, 
        // login_session, 
        delete_session,
        SessionAuthenticationError, 
        ConnectionError,
        HTTPResponseError,
        NetworkError,
        getIdToken_ms
      
      }
