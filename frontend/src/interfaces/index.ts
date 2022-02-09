export interface IUserProfile {
    email: string;
    username: string;
    disabled: boolean;
    is_superuser: boolean;
    full_name: string;
    id: string;
}

export interface IUserProfileUpdate {
    email?: string;
    username?: string;
    full_name?: string;
    password?: string;
    disabled?: boolean;
    is_superuser?: boolean;
}

export interface IUserProfileCreate {
    email: string;
    username?: string;
    full_name?: string;
    password?: string;
    disabled?: boolean;
    is_superuser?: boolean;
}
