from code.authentication import reset_password
import pandas as pd
import yaml
from yaml.loader import SafeLoader
with open('../config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

REFlabels = {
     "UoA1": "REF UoA1 - Clinical Medicine",
     "UoA2": "REF UoA2 - Public Health, Health Services and Primary Care",
     "UoA4": "REF UoA4 - Psychology, Psychiatry and Neuroscience",
     "UoA5": "REF UoA5 - Biological Sciences",
     "UoA6": "REF UoA6 - Agriculture, Food and Veterinary Sciences",
}
REFdata = {
     "UoA1": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[2,4,2,1,3,3,4,6,7,8]}),
     "UoA2": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[4,4,2,1,1,1,5,9,7,12]}),
     "UoA4": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[1,1,1,1,3,5,2,6,9,8]}),
     "UoA5": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[2,5,2,0,1,1,4,6,4,2]}),
     "UoA6": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[5,5,2,4,3,5,7,9,7,5]}),
}

def publications_over_time(data, st):
        st.subheader("Publications over time")
        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(data=data, x='Date', y='Publications', color=None, width=0, height=0, use_container_width=True)
        with col2:
            st.dataframe(data, hide_index=True, use_container_width=True, height=300)        


def render_dashboard(session_state, authenticator, st):
    st.sidebar.write(f'Logged in as *{session_state["name"]}*')
    st.sidebar.button('Change password', on_click=reset_password, args=(st,), type="primary")
    authenticator.logout('Logout', 'sidebar')
    uoas = list(config["credentials"]["usernames"][st.session_state["username"]]["uoas"]) 
    admin = config["credentials"]["usernames"][st.session_state["username"]]["admin"]
    if admin == True:
        uoas.append("admin")
    tabs = st.tabs(uoas)
    uoa = 0
    for tab in tabs:
        with tab:
            if admin == True and uoas[uoa] == "admin":
                st.header("Admin", divider="red")
                for user in list(config["credentials"]["usernames"]):
                    st.markdown(f"**User:** {user}")
                    userconfig = config["credentials"]["usernames"][user]
                    #useruoas = st.data_editor(config["credentials"]["usernames"][user]["uoas"], key=user+"uoas", num_rows="dynamic")
                    useradmin = st.toggle("Admin", value=config["credentials"]["usernames"][user]["admin"], key=user+"admin", label_visibility="visible")
                    # ===========
                    useruoas2 = {"UoA1": False, "UoA2": False, "UoA4": False, "UoA5": False, "UoA6": False, } 
                    for uoa in config["credentials"]["usernames"][user]["uoas"]:
                        useruoas2[uoa] = True
                    columns = st.columns(5)
                    colcounter = 0
                    for uoa in useruoas2.keys():
                        with columns[colcounter]:
                            useruoas2[uoa] = st.toggle(uoa, value=useruoas2[uoa], key=user+uoa, label_visibility="visible")
                        colcounter += 1
                    useruoas = [val for val in useruoas2.keys() if useruoas2[val] == True]
                    # ===========
                    config["credentials"]["usernames"][user] = {'admin': useradmin, 
                                                                'email': userconfig['email'], 
                                                                'failed_login_attempts': userconfig['failed_login_attempts'], 
                                                                'logged_in': userconfig['logged_in'], 
                                                                'name': userconfig['name'], 
                                                                'password': userconfig['password'], 
                                                                'uoas': useruoas} 
                    st.divider()
                # try:
                #     email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
                #     if email_of_registered_user:
                #         config["credentials"]["usernames"][username_of_registered_user]["uoas"] = []
                #         config["credentials"]["usernames"][username_of_registered_user]["admin"] = False
                #         with open('../config.yaml', 'w') as file:
                #             yaml.dump(config, file, default_flow_style=False)   
                #         st.success('User registered successfully')
                # except Exception as e:
                #     st.error(e)
                with open('../config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
            else: 
                # Tab content for each UoA
                st.header(REFlabels[uoas[uoa]], divider="red")
                publications_over_time(REFdata[uoas[uoa]], st)
                uoa += 1            